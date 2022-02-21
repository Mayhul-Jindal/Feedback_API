import time 
from fastapi import FastAPI, HTTPException, Response, status
import psycopg2
from psycopg2.extras import RealDictCursor
import schemas

app = FastAPI()

# --------------------------Connecting database--------------------------
while True:
    try:
        conn = psycopg2.connect(host="localhost",database="fastapi",user="postgres",password="<Your postgres instance password>",cursor_factory=RealDictCursor) # here yout credentials for the database comes
        cursor = conn.cursor()
        print('Successful connection established')
        break
    except Exception as err:
        print('Connection to database failed!!')
        print(f'Error: {err}')
        time.sleep(5)

# --------------------------function to find the post of exact id--------------------------
def find(id):
    cursor.execute(""" select * from posts where id= %s """,(id,))
    diction = cursor.fetchone() # here we know the id is unique thus using fetchone which gives us only ony entry(row)
    return diction
 
# --------------------------function to find in deleted_posts--------------------------
deleted_posts = [] # A list to store all the deleted post

def find_deleted(id):
    for object in deleted_posts: 
        diction = dict(object)
        if diction['id'] == int(id):
            return diction

# --------------------------Root GET reply--------------------------
@app.get("/")
def root():
    return {"Greetings":"Hello CSI👋."}

# --------------------------[C]reate post data--------------------------
@app.post("/post_feedback")
def post_feedback(post: schemas.Post,response: Response):
    cursor.execute(""" insert into posts ("title","content") values (%s,%s) returning * """,(post.title, post.content)) # %s is used for santization purpose to avoid any sql injections
    post = cursor.fetchone()
    conn.commit()
    response.status_code = status.HTTP_201_CREATED # status codes explained in README.md
    return {
        "message": "Feedback posted successfully" , 
        "data": post
            }

# --------------------------[R]ead all the data--------------------------
@app.get("/get_feedbacks")
def get_all_feedbacks():
    cursor.execute(""" select title,content,created_at from posts """)
    all_posts = cursor.fetchall()
    return {"data":all_posts}

# --------------------------[R]ead a specific data--------------------------
@app.get("/get_feedbacks/{id}")
def get_specific_feedback(id:  int):
    post = find(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail=f"feedback with id: {id} was not found") # this is to handle 404 error
    return {"data":post}

# --------------------------[U]pdate the data--------------------------
@app.patch("/update_feedback/{id}") # patch can be used too
def update_feedback(id: int,post: schemas.Post):
    find_post = find(id)
    if not find_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail=f"post with id: {id} was not found")
    cursor.execute(""" update posts set title=%s, content=%s, created_at=%s where id=%s returning * """,(post.title, post.content, 'now()', id))
    post  = cursor.fetchone()
    conn.commit()
    return {"message":"Feedback updated successfully",
        "data":post}

# --------------------------[Delete] the data--------------------------
@app.delete("/delete_feedback/{id}")
def delete_feedback(id: int , response: Response):
    post = find(id)
    deleted_post = find_deleted(id)
    if deleted_post:
        response.status_code = status.HTTP_204_NO_CONTENT
        return {"message":"This feedback is already deleted"}
    elif not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"feedback with id: {id} was not found")
    else:
        cursor.execute(""" delete from posts where id=%s """,(id,))
        conn.commit()
        deleted_posts.append(post)
        response.status_code = status.HTTP_200_OK
        return {"message":"Feedback deleted successfully","data":post}
