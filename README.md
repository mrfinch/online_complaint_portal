online_complaint_portal
=======================

Website for reporting various complaints like road,sewage as a part of my software enginnering project


Installation instruction:
1. Install python-pip 

2. Install django by foll: sudo pip install Django==1.6.2

3. Install postgresql: sudo apt-get install postgresql-9.3 (if 9.3 does not work try 9.2 or 9.1)

4. sudo apt-get install python-psycopg2

5. Install pgadmin3: sudo apt-get install pgadmin3

6. Create database named sen_project using pgadmin

7. Change settings.py: Edit db connections entries by changing username and password for postgres database in sen/settings.py file

8. Change MEDIA_ROOT in settings.py 
