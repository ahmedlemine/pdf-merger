## PDF Merger
A REST API built in Django and Django Rest Framework to allow users to merge PDF files. It uses PyPDF library for merging PDFs returnin a single downloadable PDF file.

I have built a [frontend](https://github.com/ahmedlemine/pdfmerger-frontend) SPA for this backend using React.js. 

For a deatiled overview of the APP (backend & forntend), please refer to this [blog post](https://pybit.es/articles/from-python-script-to-web-app-and-product/) I published on the Pybites blog.

#### API Endpoints:
Following are the API endpoints with a short description of what each does:

###### GET: /orders/
when a GET request is sent to this endpoint, it returns back a list all orders that belong to the currently authenticated user.

###### POST: /orders/
A POST request with a payload containing the merge name like: {"name": "my merge"} creates a new order (merge request).

###### GET: /orders/{uuid}/
returns details of an order identified by its id

###### DELETE /orders/{uuid}/
deletes an order

###### POST  /orders/{uuid}/add_files
A POST request with a payload containing a file add files to an order after validating file type and max files limit. It also checks to see if the order has already been merged in which case no files can be added.

###### GET /orders/{uuid}/files/
lists files of an order

###### GET /orders/{uuid}/merge/
merges order identified by its id.
This is where the core feature of the app lives. This view/endpoint does some initial checks to verify that the order has at least 2 files to merge and has not been previously merged then it hands work over to a utility function that preforms the actual merging of all PDF files associated with the order. 
Nothing fancy here, the function takes a list of PDF files, merges them using [PyPDF](https://pypi.org/project/pypdf/) and returns the path for the merged PDF. On a successful merge, the view takes the path and sets it as the value for *download_url* property of the order instance for the next endpoint to use. It also marks the order and all of its files as merged. This can be used to cleanup all merged orders and their associated files to save server space.

###### GET /orders/{uuid}/download/
download the merged PDF of an order after verifying that it has been merged and ready for download. The API allows a max number of downloads of each order and max time on server. This prevents users from keeping merged files on the server forever and sharing the links, turning the app basically into a free file sharing service.

###### DELETE /files/{uuid}/
delete a file identified by its id


### Auth & Permissions Endpoints
The API implements JWT auth using [Djoser](https://github.com/sunscrapers/djoser) which is a REST implementation of Django's auth system.
The following endpoints are available for auth:
- GET /auth/users/ : lists all users if you're an admin. Only returns your user info if you aren't admin.
- POST /auth/users/ : a POST request with a payload containing: name, email and password will register a new user.
- POST /auth/jwt/create: a POST request with a payload containing: email and password will return access and refresh tokens to use for authenticating subsequent requests.
- POST /auth/refresh : a POST request with a payload containing: the *refresh* token will return a new access token.
as well as some other useful endpoints for changing and resetting passwords.

### What can be improved:
- currently, the backend only offers the absolute minimum feature of PyPDF: merging whole PDFs. This can be improved by allowing users to insert whole or part of a PDF after a specific page of another PDF, split PDFs or by adding any of the many great features PyPDF offers.
- for now the frontend allows the user to list all his past merges, delete them, or download them instead of merging them again. However the API is built so that the merge is archived after either max download times or time since created (both can be set in settings.py) otherwise users can use your app as a free cloud by uploading files, merging them, then sharing the download link. Ideally I'd like to setup a cron job and a management command to automate deleting archived orders and a related PDF files to save space on server.
- adding tests both for backend and frontend.
- adding documentation for the API.