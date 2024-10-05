 # async FastAPI Store

English | [Русский](README.RU.md)

The project is a demo FastAPI service developed using Clean Architecture.

FastAPI is an asynchronous framework that is based on the Starlette web framework and uses asyncio, Pydantic data validation library.
Thanks to strict typing, the framework has built-in OpenAPI file generation.
After launching the application, you will receive ready-made documentation for your API and an interface for viewing it.

FastAPI does not have a pre-defined project structure.
Here, divides the project by file type (crud, models etc.), which works well for microservices or projects with fewer scopes.
