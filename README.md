#Upwork notifier

Script workflow:

1. Establishing the connection with the server.

2. The user, whose account is logged in at the moment, gets an access to work with our script (i.e. before running the script you need to go to the browser and log in to some profile, the tab should not be incognito, the login should remain active even if the page was closed)

3. Gets the current user ID

4. Gets the ID’s of all clients with whom we had a conversations previously in the current profile

5. Gets the Client Name and the Job Link from the “Messages” section.
    
    a.Retrieves the name of the last done job by a given client from the “Client’s recent activity” list

6. Gets links to all new jobs at the UpWork
    
    a.Retrieves the name of the last done job by a given client from the “Client’s recent activity” list.

7. Compares the data obtained in paragraph 5.a and paragraph 6.a.

8. If the names of the last done jobs for the customers coincided, it means that we have already talked with this client. if there is a match a notification is sending to Slack in the form Client Name: Job Link
