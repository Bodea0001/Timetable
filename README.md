1. You need to create and run a virtual environment with your python interpreter version (use python3.10 and above) (you can skip this step if the virtual environment has already been created)
   <br>
   `python3.10 -m venv env`
2. You need to run a virtual environment
   <br>
   `source env/bin/activate`
3. You need to download libraries (you can skip this step if the librariesare downloaded)
   <br>
   `pip install -r requirements.txt`
4. You need to download **Postgresql**
5. You need to declare environment varialbes so that they appear in **config.py**.
6. You need to run **models.py** to create models in the database.
   `python models.py`
7. Now you can start the project
   `uvicorn index:app --reload`