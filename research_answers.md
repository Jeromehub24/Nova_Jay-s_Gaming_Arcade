# Research Answers

## 1. Python requests module

The `requests` module is a Python library that makes HTTP requests easier to work with. Instead of manually dealing with lower-level networking steps, it gives a cleaner way to send `GET`, `POST`, `PUT`, and `DELETE` requests. It is useful when a Python program needs to talk to a web API or download data from another service.

In a normal project, I would use `requests.get()` to fetch data, `requests.post()` to send data, and then read the response with things like `response.status_code`, `response.text`, or `response.json()`. One reason it is popular is that the code is short and easy to read. It also supports headers, authentication, query parameters, JSON payloads, and timeouts, which makes it a practical tool for API integration.

## 2. JSON and XML

### JSON

JSON is a text format used to store and send structured data. It is very common in web APIs because it is lightweight and easy to read in both JavaScript and Python.

#### Advantages of JSON
- It is shorter and less cluttered than XML.
- It is easy to convert into Python dictionaries and lists.
- It is widely used by modern APIs and web apps.
- It is easier for people to read quickly.

#### Disadvantages of JSON
- It does not handle comments well in normal use.
- It is less strict about structure than XML.
- It is not ideal when a project needs very rich metadata.
- It can become hard to read when deeply nested.

### XML

XML is also a text format for storing and transferring data, but it uses tags and a stricter structure. It is older than JSON and is still used in some enterprise systems and document-heavy systems.

#### Advantages of XML
- It has a clear tagged structure.
- It works well when documents need metadata and attributes.
- It supports validation with schemas.
- It is useful in systems that already depend on XML standards.

#### Disadvantages of XML
- It is more verbose than JSON.
- It usually takes more time to write and read.
- It can feel heavy for simple API responses.
- It is less common than JSON in newer web projects.

## 3. RESTful APIs

A RESTful API is an API that follows REST principles. In simple terms, it uses URLs to represent resources and uses HTTP methods like `GET`, `POST`, `PUT`, and `DELETE` to work with those resources. A client sends a request, the server processes it, and the API returns data, usually in JSON.

RESTful APIs work well because they are stateless. That means each request should contain the information needed for that request, instead of depending on hidden server-side request history. This makes the API easier to scale and easier for other systems to use.

#### Advantages of RESTful APIs
- They are easy to understand because they match standard HTTP actions.
- They are flexible for web, mobile, and third-party clients.
- They scale well because requests are stateless.
- They are widely supported with good tooling.

#### Disadvantages of RESTful APIs
- Endpoint design can become messy if it is not planned properly.
- Multiple requests may be needed to gather related data.
- Different teams may build REST APIs in inconsistent ways.
- Security and permissions still need careful work even if the structure is simple.
