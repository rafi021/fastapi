from fastapi import FastAPI
from pydantic import BaseModel
from schemas.postschema import PostCreateSchema, PostResponse

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/posts", response_model=list[PostResponse])
def read_posts():
    # Here you would typically retrieve all posts from the database
    return [
        PostResponse(id=1, title="Sample Post 1", content="This is a sample post.", author="Author Name", created_at="2024-01-01T00:00:00Z", updated_at="2024-01-01T00:00:00Z"),
        PostResponse(id=2, title="Sample Post 2", content="This is another sample post.", author="Author Name", created_at="2024-01-01T00:00:00Z", updated_at="2024-01-01T00:00:00Z")
    ]

# Posts routes
@app.post("/posts/", response_model=PostResponse)
def create_post(post: PostCreateSchema):
    # Here you would typically save the post to the database and return the created post
    return PostResponse(id=1, title=post.title, content=post.content, author=post.author, created_at="2024-01-01T00:00:00Z", updated_at="2024-01-01T00:00:00Z")

@app.get("/posts/{post_id}", response_model=PostResponse)
def read_post(post_id: int):
    # Here you would typically retrieve the post from the database using the post_id
    return PostResponse(id=post_id, title="Sample Post", content="This is a sample post.", author="Author Name", created_at="2024-01-01T00:00:00Z", updated_at="2024-01-01T00:00:00Z")

@app.put("/posts/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post: PostCreateSchema):
    # Here you would typically update the post in the database using the post_id and return the updated post
    return PostResponse(id=post_id, title=post.title, content=post.content, author=post.author, created_at="2024-01-01T00:00:00Z", updated_at="2024-01-02T00:00:00Z")

@app.delete("/posts/{post_id}")
def delete_post(post_id: int):
    # Here you would typically delete the post from the database using the post_id
    return {"message": f"Post with id {post_id} has been deleted."}