<strong> **DO NOT DISTRIBUTE OR PUBLICLY POST SOLUTIONS TO THESE LABS. MAKE ALL FORKS OF THIS REPOSITORY WITH SOLUTION CODE PRIVATE. PLEASE REFER TO THE STUDENT CODE OF CONDUCT AND ETHICAL EXPECTATIONS FOR COLLEGE OF INFORMATION TECHNOLOGY STUDENTS FOR SPECIFICS. ** </strong>
# WESTERN GOVERNORS UNIVERSITY 
## D602 – TASK 3
Welcome to Task 3! 
For specific task instructions and requirements for this assessment, please refer to the course page.


## Continous Testing and Delivery 
This course has a `.gitlab-ci.yml` file which has been configured to automatically run the tests you write as part of this course as soon as you push your work to this GitLab projects, and build a Docker image for evaluation. 

You can see the status of these tests by clicking on the "Build" menu on the left, then selecting the "Pipelines" menu item. Results of these tests are for your benefit, please do not alter the `.gitlab-ci.yml` file.

## Container Registry and Docker
As part of this task, you will need to demonstrate a running container, the `.gitlab-ci.yml` file provided for you will produce the image for this container for you. 

You can do it locally using `docker build`, but to pull the container produced by the `.gitlab-ci.yml` file, you must first log into GitLab using the `docker login registry.gitlab.com` command. This will not accept your WGU password, so you must configure a [Personal Access Token](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html#create-a-personal-access-token). 

To create a Personal Access Token:

1. Click on `Search or go to...` on the left sidebar
2. Go to your GitLab profile settings
3. Navigate to "Access Tokens" in the left sidebar
4. Create a new token with the "read_registry" scope
5. Copy the generated token
6. Save the token somewhere, you cannot get it back again later, and will have to create new one if you lose it

Once you have your Personal Access Token, you can log in to the GitLab Container Registry using:

```
docker login registry.gitlab.com -u <your-gitlab-username>
```

Once logged in, you can pull the container by going to the Deploy --> Container Registry section of this project in the left sidebar then clicking on the copy button for your container image URL. Once you have the URL for your contaer image, run:

```
docker pull <your-container-image-url>
```

You can then run the container using:

```
docker run -p 8000:8000 <your-container-image-url>
```

This will launch the API on localhost 127.0.0.1, port 8000.

