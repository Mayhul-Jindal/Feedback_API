from pydantic import BaseModel
# --------Pydantic data below--------

# This is to create a scheme for POST data
class Post(BaseModel):
    title: str
    content: str

    