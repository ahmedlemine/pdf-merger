## PDF Merger
A basic rest-ish API for the backend that allows you to create an order (a merge request), add files to it, merge the files  and get back a single PDF file to download and use.
Ther is also a simple [frontend](https://github.com/ahmedlemine/pdfmerger-frontend) for it using React.js.

The backend is built with Django and Django Rest Framework. The actual merging of PDFs is done using PyPDF2 which is now just [PyPDF](https://pypi.org/project/pypdf/).

The app includes user auth with JWT (using "djoser") so that each user's docs are private and not accessible by other user. Also this allows the app to be expanded to a paid service or target larger userbase like using it as an internal tool in your company, hence the use of "order" to indicate how many orders the user's account allows etc.

The frontend is built using React JS. The user can signup/login and merge PDF files in a very simple process which at the end gives a downloadable PDF.

This is just a tool that works and does the job. It's far from perfect or ready for public use.

### What can be improved:
- Currently, the backend only offers the absolute minimum feature of PyPDF: merging whole PDFs. This can be improved by allowing users to insert whole or part of a PDF after a specific page of another PDF, split PDFs or by adding any of the many great features PyPDF offers.

- For now the frontend allows the user to list all his past merges, delete them, or download them instead of merging them again. However the API is built so that the merge is archived after either max download times or time since created (both can be set in settings.py) otherwise users can use your app as a free cloud by uploading files, merging them, then sharing the download link. Ideally I'd like to setup a cron job and a management command to automate deleting archived orders and a related PDF files to save space on server.


The back/front ends are kept in separate repos as they aren't necessarily connected to each other. Someone can take just the backend and build whatever frontend they like for it.

There are Dockerfile and a docker-compose files for back/front ends. They are fine for development/local deployment but they are not for production.
