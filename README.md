<div id="top"></div>

<h3 align="center">image-thumbnail-api</h1>
<p align="center">A REST API that processes images and returns thumbnails of them in different sizes, based on user's tier.</p>

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#tiers">Tiers</a></li>
    <li><a href="#endpoints">Endpoints</a></li>
    <li><a href="#testing">Testing</a></li>
  </ol>
</details>

## Getting Started
This is how to make the project run locally.
### Installation

1. Clone the repo
  ```
  git clone https://github.com/ikolokotronis/image-thumbnail-api.git
  ```
2. Move to docker directory (assuming you are located in the project's root directory)
  ```
  cd image_thumbnail_api/
  cd .docker/
  ```
3. Build the container
  ```
  docker-compose up --build
  ```
4. Now you can access the API at http://127.0.0.1:8080

## Tiers

There are three bultin account tiers: Basic, Premium and Enterprise:
<ul>
<li>users that have "Basic" plan after uploading an image get: </li>
<ul>
<li>a link to a thumbnail that's 200px in height</li>
</ul>
<li>users that have "Premium" plan get:</li>
<ul>
<li>a link to a thumbnail that's 200px in height</li>
<li>a link to a thumbnail that's 400px in height</li>
<li>a link to the originally uploaded image</li>
</ul>
<li>users that have "Enterprise" plan get</li>
<ul>
<li>a link to a thumbnail that's 200px in height</li>
<li>a link to a thumbnail that's 400px in height</li>
<li>a link to the originally uploaded image</li>
<li>ability to fetch a link to the (binary) image that expires after a number of seconds (user can specify any number between 300 and 30000)</li>
</ul>
</ul>

Apart from the builtin tiers, admins are able to create arbitrary tiers with the following things configurable:
* arbitrary thumbnail sizes
* presence of the link to the originally uploaded file
* ability to generate expiring links


## Endpoints

All endpoints besides <a href="#expiring-images">Expiring Images</a> require a valid token to be included in the header of the
request.   
A token is generated for each user when they are created/registered, and can be acquired from the Token model in django-admin, 
or from the Token table in the database.  
  
Header with authorization token example: 
```
Authorization: Token b5d557e29ac73caf047db17c7a28b6e962ff0dfc  # This token is only for explainatory purposes and won't work in a real request.
```

### Media access endponts

#### Standard Images
GET `media/<int:user_pk>/images/<str:file_name>`

#### Expiring Images
GET `media/expiring-images/<str:file_name>`

<br/>

### Getting all images
`GET /images/`
<br/>
<br/>
Images available for the user are determined by the token included in the header of the request.  

Response example:
```
[
    {
        "pk": 27,
        "original_image": "/media/1/images/test.jpg",
        "created_at": "2022-06-21T23:21:22.467379Z"
    },
    {
        "pk": 28,
        "original_image": "/media/1/images/test_UkadI7r.jpg",
        "created_at": "2022-06-23T12:35:44.317739Z"
    },
    {
        "pk": 29,
        "original_image": "/media/1/images/test_W0gfr22.jpg",
        "created_at": "2022-06-23T13:00:54.707904Z"
    },
    {
        "pk": 30,
        "original_image": "/media/1/images/test_WmeDTuE.jpg",
        "created_at": "2022-06-23T13:01:25.230068Z"
    }
]
```

<br/>

### Uploading images
`POST /images/`
<br/>
<br/>
Uploading images require a `original_image` field to be included in the body.  As a value, it expects an image file in png or jpg format.  
Any other values will be rejected.  
#### Important note:
If user's tier comes with ability to fetch expiring links, there shoud also be a `live_time` field in the body, 
determining the amount of seconds the link will be available before it expires. Number range should be between 300 and 30000.  
  
Request example (assuming user tier is Enterprise):

#### Header
```
Authorization: Token b5d557e29ac73caf047db17c7a28b6e962ff0dfc,
Content-Type: multipart/form-data
```

#### Body
```
{
  "original_image": test.jpg,
  "live_time": "500"
}
```
Response differs depending on which tier user currently has.  
Response example (assuming user tier is Enterprise):  
```
{
    "400px_thumbnail": "/media/1/images/test_ioN602N_400px_thumbnail.jpg",
    "200px_thumbnail": "/media/1/images/test_ioN602N_200px_thumbnail.jpg",
    "original_image": "/media/1/images/test_ioN602N.jpg",
    "500s_expiring_link": "/media/expiring-images/test_ioN602N.jpg",
    "success": "Image uploaded successfully"
}
```

### Testing
Because the app has no registration functionality, a testing admin user is created upon every container build.   
To access the account, use these credentials:  
* <b>username</b>: admin  
* <b>password</b>: admin
  
To access the token that was generated for this account, go to django-admin and view the Token model.  
You can use it in your request headers.

<p align="right">(<a href="#top">back to top</a>)</p>
