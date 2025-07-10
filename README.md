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


From github:

1. clone this repository

```
https://github.com/brilbrilbril/nawatech_test_case2.git
```

2. head to the project root

```
cd nawatech_test_case2
```

3. create virtual environmentand activate it

```
python -m venv venv

venv\Scripts\activate
```

4. install all dependencies

```
pip install -r requirements.txt
```

5. create .env file with the contents:

```
GOOGLE_API_KEY=your-api-key
```

6. run streamlit app

```
streamlit run app/main.py
```