from fastapi import FastAPI, Query, Response
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

#Q1
@app.get("/")
def home():
    return {"message": "Welcome to City Public Library"}

#Q2
books = [
    {"id": 1, "title": "Python Basics", "author": "John", "genre": "Tech", "is_available": True},
    {"id": 2, "title": "History of India", "author": "Ravi", "genre": "History", "is_available": True},
    {"id": 3, "title": "Science Today", "author": "Meena", "genre": "Science", "is_available": False},
    {"id": 4, "title": "AI Future", "author": "Kiran", "genre": "Tech", "is_available": True},
    {"id": 5, "title": "World War", "author": "David", "genre": "History", "is_available": False},
    {"id": 6, "title": "Fiction Story", "author": "Anu", "genre": "Fiction", "is_available": True}
]


#Q6
class BorrowerRequest(BaseModel):
    member_name: str = Field(..., min_length=2)
    book_id: int = Field(..., gt=0)
    borrow_days: int = Field(..., gt=0)
    member_id: str = Field(..., min_length=4)
    member_type: str = "regular"

class NewBook(BaseModel):
    title: str = Field(..., min_length=2)
    author: str = Field(..., min_length=2)
    genre: str = Field(..., min_length=2)
    is_available: bool = True
    

#Q7
def find_book(book_id):
    for book in books:
        if book["id"] == book_id:
            return book
    return None

def calculate_due_date(borrow_days, member_type):
    if member_type == "premium":
        return f"Return by: Day {15 + borrow_days} (Premium)"
    else:
        return f"Return by: Day {15 + borrow_days}"


@app.get("/books")
def get_books():
    total = len(books)
    available_cnt = len([b for b in books if b["is_available"]])
    return {
        "total": total,
        "available_cnt": available_cnt,
        "books": books
    }
    

#Q5
@app.get("/books/summary")
def books_summary():
    total = len(books)
    available = len([b for b in books if b["is_available"]])
    borrowed = total - available
    
    genre_cnt = {}
    for book in books:
        genre = book["genre"]
        if genre in genre_cnt:
            genre_cnt[genre] += 1
        else:
            genre_cnt[genre] = 1
    return {
        "total_books": total,
        "available_books": available,
        "borrowed_books": borrowed,
        "genre_cnt": genre_cnt
    }


@app.get("/books/filter")
def filter_books(
    genre: str = Query(None),
    author: str = Query(None),
    is_available: bool = Query(None)
):
    filtered = filter_book(genre, author, is_available)
    return{
        "total": len(filtered),
        "books": filtered
    }


#Q16
@app.get("/books/search")
def search_books(keyword: str):
    result = []
    
    for book in books:
        if (keyword.lower() in book["title"].lower() or keyword.lower() in book["author"].lower()):
            result.append(book)
        if not result:
            return {"message": "No books found"}
        return {
            "total_found": len(result),
            "books": result
        }
        

#Q17
@app.get("/books/sort")
def sort_books(sort_by: str = "title", order: str = "asc"):
    if sort_by not in ["title", "author", "genre"]:
        return{"error": "Invalid sort_by value"}
    if order not in ["asc", "desc"]:
        return {"error": "Invalid order value"}
    sorted_books = sorted(books, key=lambda x: x[sort_by])
    if order == "desc":
        sorted_books.reverse()
    return {
        "sort_by": sort_by,
        "order": order,
        "books": sorted_books
    }


#Q18
@app.get("/books/page")
def paginate_books(page: int = 1, limit: int = 3):
    total = len(books)
    
    start = (page - 1) * limit
    end = start + limit
    
    paginated = books[start:end]
    total_pages = (total + limit - 1) // limit
    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "books": paginated
    }


#Q3
@app.get("/books/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book
    return {"error": "Book not found"}


#Q4
borrow_records = []
record_cnt = 1
queue = []

@app.get("/borrow-records")
def get_borrow_records():
    return {
        "total": len(borrow_records),
        "records": borrow_records
    }



#Q19
@app.get("/borrow-records/search")
def search_records(member_name: str):
    result = []
    for record in borrow_records:
        if member_name.lower() in record["member_name"].lower():
            result.append(record)
    if not result:
        return {"message":"No records found"}
    return{
        "total_found": len(result),
        "records": result
    }

@app.get("/borrow-records/sort")
def sort_records(order: str = "asc"):
    if order not in ["asc", "desc"]:
        return{"error": "Invalid order"}
    sort_records = sorted(borrow_records, key=lambda x: x["borrow_days"])
    if order == "desc":
        sort_records.reverse()
    return{
        "order": order,
        "records": sort_records
    }


#Q20
@app.get("/borrow-records/advanced")
def advanced_records(
    keyword: str = "",
    order: str = "asc",
    page: int = 1,
    limit: int = 2
):
    filtered = []
    for record in borrow_records:
        if keyword.lower() in record["member_name"].lower():
            filtered.append(record)
    if order not in ["asc", "desc"]:
        return{"error": "Invalid order"}
    filtered = sorted(filtered, key=lambda x:x["borrow_days"])
    if order == "desc":
        filtered.reverse()
        
    total = len(filtered)
    start = (page - 1) * limit
    end = start + limit
    paginated = filtered[start:end]
    total_pages = (total + limit - 1) // limit
    
    return{
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "records": paginated
    }



#Q8
@app.post("/borrow")
def borrow_book(request: BorrowerRequest):
    global record_cnt
    
    book = find_book(request.book_id)
    if not book:
        return {"error": "Book not found"}
    
    if not book["is_available"]:
        return {"error": "Book is already borrowed"}
    
    book["is_available"] = False
    
    if request.member_type == "regular" and request.borrow_days > 30:
        return {"error": "Regular members can borrow max 30 days"}
    
    if request.member_type == "premium" and request.borrow_days > 60:
        return {"error": "Premium members can borrow max 60 days"}
    due_date = calculate_due_date(request.borrow_days, request.member_type)
    
    record = {
        "record_id": record_cnt,
        "member_name": request.member_name,
        "member_id": request.member_id,
        "book_id": request.book_id,
        "book_title": book["title"],
        "borrow_days": request.borrow_days,
        "due_date": due_date
    }
    borrow_records.append(record)
    record_cnt += 1
    
    return record

#Q9
def filter_book(genre=None, author=None, is_available=None):
    result = books
    
    if genre is not None:
        result = [b for b in result if b["genre"].lower() == genre.lower()]
    if author is not None:
        result = [b for b in result if b["author"].lower() == author.lower()]
    if is_available is not None:
        result = [b for b in result if b["is_available"] == is_available]
    return result


#Q11
@app.post("/books")
def add_book(new_book: NewBook, response: Response):
    for book in books:
        if book["title"].lower() == new_book.title.lower():
            return {"error": "Book with this title already exists"}
    new_id = len(books) + 1
    book = {
        "id": new_id,
        "title": new_book.title,
        "author": new_book.author,
        "genre": new_book.genre,
        "is_available": new_book.is_available
    }
    books.append(book)
    
    response.status_code = 201
    return book

#Q12
@app.put("/books/{book_id}")
def update_book(
    book_id: int,
    genre: Optional[str] = None,
    is_available: Optional[bool] = None
):
    book = find_book(book_id)
    if not book:
        return {"error": "Book not found"}
    if genre is not None:
        book["genre"] = genre
    if is_available is not None:
        book["is_available"] = is_available
    return book



#Q13
@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    book = find_book(book_id)
    if not book:
        return{"error": "Book not found"}
    books.remove(book)
    return{"message": f"Book '{book['title']}' deleted successfully"}


#Q14
@app.post("/queue/add")
def add_to_queue(member_name: str, book_id: int):
    book = find_book(book_id)
    if not book:
        return{"error":"Book not found"}
    if book["is_available"]:
        return{"error": "Book is available, no need to queue"}
    queue.append({
        "member_name": member_name,
        "book_id": book_id
    })
    return {"message": "Added to queue", "queue":queue}

@app.get("/queue")
def get_queue():
    return{
        "total": len(queue),
        "queue": queue
    }


#Q15
@app.post("/return/{book_id}")
def return_book(book_id: int):
    book = find_book(book_id)
    if not book:
        return{"error": "Book not found"}
    book["is_available"] = True
    for person in queue:
        if person["book_id"] == book_id:
            queue.remove(person)
            book["is_available"] = False
            record = {
                "record_is": len(borrow_records) + 1,
                "member_name": person["member_name"],
                "book_id": book_id,
                "book_title": book["title"],
                "borrow_days": 5,
                "due_date": calculate_due_date(5,"regular")
            }
            borrow_records.append(record)
            
            return{
                "message": "Book returned and reassigned",
                "assigned_to": person["member_name"]
            }
            
    return {"message": "Book returned and now available"}