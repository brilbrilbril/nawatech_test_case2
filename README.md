Installation steps:

From docker:
1. Open terminal
2. Pull the image using this command:

```
docker pull brillyando/nawatech_case2:latest
```

3. create .env file that consists of google api key

```
GOOGLE_API_KEY=your-api-key
```

4. run the pulled image by executing:
```
docker run --env-file .env -p 8501:8501 brillyando/nawatech_case2:latest
```

OR if you don't want to create .env file

```
docker run -e GOOGLE_API_KEY=yourapi_key -p 8501:8501 brillyando/nawatech_case2:latest
```


From github:
1. 