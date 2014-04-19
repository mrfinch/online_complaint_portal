online_complaint_portal
=======================

The website is Anand Complaint Portal , a common platform for the people and the municipality staff to interact on complaint issues of the respective area.



Installation instructions for Linux:

1. Install python-pip 

2. Install django by following: 
   
   $sudo pip install Django==1.6.2

3. Install postgresql-9.3(if 9.3 does not work try 9.2 or 9.1): 
    
   $sudo apt-get install postgresql-9.3 

4. Install python-psycopg2
    
   $sudo apt-get install python-psycopg2

5. Install pgadmin3: s
  
   $sudo apt-get install pgadmin3

6. In pgadmin3 create an empty database named sen_final.

7. Go to online_complaint_portal/sen/settings.py file and change settings.py.
   Find DATABASES. 
   Edit db connections entries by changing USER and PASSWORD field for postgres database you have created in pgadmin3 in    sen/settings.py file

8. Change MEDIA_ROOT in settings.py.
   Find

   MEDIA_ROOT='/home/Mrfinch/online_complaint_portal/complaint_portal/static/'

   Replace the above with the path to static folder in online_complaint_portal.
   
9. Go to the terminal and change your directory to online_complaint_portal and run the following :
   
   $ python manage.py syncdb
   
   The command asks you to make a superuser of the database. Enter the username and password you want to enter.

10. Run the local host server to run the website in your browser using the following command in the terminal :

   $ python manage.py runserver
   
11. Go to your browser and go to url localhost:8000/complaint_potal/index to visit the home page. To directly view any      other url , visit the urls.py file in the folder to know the name of the respective url.

    



