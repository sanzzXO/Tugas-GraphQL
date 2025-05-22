
from flask import Flask
from flask_graphql import GraphQLView
import graphene
from graphene import ObjectType, String, Int, List, Field, Mutation

authors = [
    {"id": "1", "name": "J.K. Rowling"},
    {"id": "2", "name": "George Orwell"},
    {"id": "3", "name": "J.R.R. Tolkien"}
]

books = [
    {"id": "1", "title": "Harry Potter and the Philosopher's Stone", "author_id": "1", "year": 1997},
    {"id": "2", "title": "1984", "author_id": "2", "year": 1949},
    {"id": "3", "title": "Animal Farm", "author_id": "2", "year": 1945},
    {"id": "4", "title": "The Hobbit", "author_id": "3", "year": 1937},
    {"id": "5", "title": "The Lord of the Rings", "author_id": "3", "year": 1954}
]

class Author(ObjectType):
    id = String()
    name = String()
    

class Book(ObjectType):
    id = String()
    title = String()
    year = Int()
    author = Field(Author)
    
    def resolve_author(self, info):
        author_id = self.get('author_id')
        for author in authors:
            if author["id"] == author_id:
                return author
        return None

class CreateBook(Mutation):
    class Arguments:
        title = String(required=True)
        author_id = String(required=True)
        year = Int(required=True)
    
    book = Field(lambda: Book)
    
    def mutate(self, info, title, author_id, year):
        author_exists = False
        for author in authors:
            if author["id"] == author_id:
                author_exists = True
                break
        
        if not author_exists:
            raise Exception(f"Author with id {author_id} not found")
        
        new_id = str(len(books) + 1)
        new_book = {
            "id": new_id,
            "title": title,
            "author_id": author_id,
            "year": year
        }
        books.append(new_book)
        return CreateBook(book=new_book)

class CreateAuthor(Mutation):
    class Arguments:
        name = String(required=True)
    
    author = Field(lambda: Author)
    
    def mutate(self, info, name):
        new_id = str(len(authors) + 1)
        new_author = {
            "id": new_id,
            "name": name
        }
        authors.append(new_author)
        return CreateAuthor(author=new_author)

class Mutations(ObjectType):
    create_book = CreateBook.Field()
    create_author = CreateAuthor.Field()

class Query(ObjectType):
    book = Field(Book, id=String(required=True))
    books = List(Book)
    author = Field(Author, id=String(required=True))
    authors = List(Author)
    
    def resolve_book(self, info, id):
        for book in books:
            if book["id"] == id:
                return book
        return None
    
    def resolve_books(self, info):
        return books
    
    def resolve_author(self, info, id):
        for author in authors:
            if author["id"] == id:
                return author
        return None
    
    def resolve_authors(self, info):
        return authors

schema = graphene.Schema(query=Query, mutation=Mutations)

app = Flask(__name__)

app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True  
    )
)

# Add a simple route to the root URL
@app.route('/')
def index():
    return """
    <h1>Flask GraphQL API</h1>
    <p>This is a simple GraphQL API built with Flask and Graphene.</p>
    <p>Go to <a href="/graphql">/graphql</a> to access the GraphiQL interface.</p>
    """

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')