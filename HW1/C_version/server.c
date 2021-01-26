// Server side implementation of UDP client-server model 
#include <stdio.h> 
#include <stdlib.h> 
#include <unistd.h> 
#include <string.h> 
#include <sys/types.h> 
#include <sys/socket.h> 
#include <arpa/inet.h> 
#include <netinet/in.h> 
#include <sqlite3.h> 
#include <time.h> 
#include <stdbool.h>

#define BUF_SIZE 1024
int max(int x, int y) 
{ 
	if (x > y) 
		return x; 
	else
		return y; 
} 
void message_handle(char *recvbuf, char *sendbuf, bool* login, char* name);
void user_register(char **receive, char *send);
int user_login(char **receive, char *send, char *name);//return 1:login
int user_logout(char **receive, char *send, char *name);
void whoami(char **receive, char *send);
void userList(char **receive, char *send);
void createDB();
static int callback(void *NotUsed, int argc, char **argv, char **azColName);

// Driver code 
int main(int argc , char *argv[]) { 
	//*usernumber=0;
	int UDP_fd, TCP_fd, forClientSockfd, nready, maxfdp1; 
	fd_set rset;
	char sendbuf[BUF_SIZE],recvbuf[BUF_SIZE]; 
	struct sockaddr_in serverinfo, clientinfo; 
	pid_t childpid; 

		/*先開DB*/
	createDB();
	
		/*開始連線設定*/
	//設定執行client之格式為./server host ex ./server 7890 
	if (argc != 2) {
    fprintf(stderr, "Usage: %s host \n", argv[0]);//argv[0]為./client
    exit(EXIT_FAILURE);//關掉程式
    }

    //建立TCP socket file descriptor
    TCP_fd = socket(AF_INET, SOCK_STREAM, 0); 
	if (UDP_fd == -1){
    perror("Fail to create a UDP socket.");
    exit(EXIT_FAILURE);
	}

	//建立UDP socket file descriptor
	UDP_fd = socket(AF_INET , SOCK_DGRAM , 0);
	if (UDP_fd == -1){
        perror("Fail to create a UDP socket.");
        exit(EXIT_FAILURE);
    }
	
	//sockaddr_in設定
	memset(&serverinfo, 0, sizeof(serverinfo)); 
	memset(&clientinfo, 0, sizeof(clientinfo)); 
	serverinfo.sin_family = AF_INET; // IPv4 
	serverinfo.sin_addr.s_addr = INADDR_ANY; 
	serverinfo.sin_port = htons(atoi(argv[1])); 
	
	// Bind TCP
	if ( bind(TCP_fd, (const struct sockaddr *)&serverinfo, sizeof(serverinfo)) < 0 )
	{
		perror("TCP bind failed"); 
		exit(EXIT_FAILURE); 		
	} 
	listen(TCP_fd, 10); 

	// Bind UDP 
	if ( bind(UDP_fd, (const struct sockaddr *)&serverinfo, sizeof(serverinfo)) < 0 ) 
	{ 
		perror("UDP bind failed"); 
		exit(EXIT_FAILURE); 
	}
	// clear the descriptor set 
	FD_ZERO(&rset);  

	// get maxfd 
	maxfdp1 = max(TCP_fd, UDP_fd) + 1;


	int addrlen, n; 
	addrlen = sizeof(clientinfo);  

	while(1){

		// set TCPfd and UDPfd in readset 
		FD_SET(TCP_fd, &rset); 
		FD_SET(UDP_fd, &rset);

		// select the ready descriptor 
		nready = select(maxfdp1, &rset, NULL, NULL, NULL);

		//tcp process
		if (FD_ISSET(TCP_fd, &rset)) { 
			forClientSockfd = accept(TCP_fd, (struct sockaddr*)&clientinfo, (socklen_t*)&addrlen); 
			if(forClientSockfd!=-1) printf("New connection.\n");
			if ((childpid = fork()) == 0) {
				bool login=0;
				char name[50];
				close(TCP_fd);//不需要了
				while(1){
	                bzero(sendbuf, sizeof(sendbuf));
					bzero(recvbuf, sizeof(recvbuf)); 
					read(forClientSockfd, recvbuf, sizeof(recvbuf)); 

					if(strcmp("",recvbuf)==0) continue; //不理會空字串
					//printf("%s\n ", recvbuf);
	                
	                message_handle(recvbuf,sendbuf, &login,name);
	                if(strncmp(sendbuf,"end",3)==0){
						write(forClientSockfd, (const char*)sendbuf, sizeof(sendbuf));
						close(forClientSockfd);
						forClientSockfd=-1;
	                	break;
	                }
	                else write(forClientSockfd, (const char*)sendbuf, sizeof(sendbuf));
					
				}
				
			} 
			//printf("in parent: close forClientSockfd\n" );
            close(forClientSockfd);
        }  
				 
 		//udp
		if (FD_ISSET(UDP_fd, &rset)) {
			bzero(recvbuf, sizeof(recvbuf));  
			n = recvfrom(UDP_fd, recvbuf, sizeof(recvbuf), 0, (struct sockaddr*)&clientinfo, (socklen_t*)&addrlen); 
			message_handle(recvbuf,sendbuf,0,NULL);
			//fgets(sendbuf, sizeof(sendbuf), stdin);
			sendto(UDP_fd, sendbuf, sizeof(sendbuf), 0,(const struct sockaddr*)&clientinfo, addrlen); 
		} 
		

	}
	
	return 0; 
}

void message_handle(char *recvbuf, char *sendbuf, bool* login, char* name){
	char  string[500];
	strcpy(string,recvbuf);
    char * token = strtok(string, " ");
    char* message[4];
    int i=0, word_cnt=0;
    while( token != NULL ) {
        message[i] = token;
        i++; word_cnt++;
        token = strtok(NULL, " ");
    }
    if(strncmp(message[0], "register", 8) == 0){
        if(word_cnt == 4) {
        	user_register(message, sendbuf);
        	return;
        }
        else {
        	strcpy(sendbuf,"Usage: register <username> <email> <password>\n");
        	return;
        }
    }
    else if(strncmp(message[0], "login", 5) == 0){
        if(word_cnt == 3 && *login==0) {
			*login=user_login(message,sendbuf,name);
        	return;
        }
        else if (*login==1){
        	strcpy(sendbuf,"Please logout first.\n");
        	return;
        }
        else {
        	strcpy(sendbuf,"Usage: login <username> <password> \n");
        	return;
        } 
    }
	else if(strncmp(message[0], "logout", 6) == 0){
	    if(word_cnt == 1 && *login==1) {
	    	*login=user_logout(message,sendbuf,name);
	    	return;
	    }
	    else if (*login==0){
		strcpy(sendbuf,"Please login first.\n");
		return;
		}
        else {
        	strcpy(sendbuf,"Usage: logout\n");
        	return;
        } 
	}
    else if(strncmp(message[0], "whoami", 6) == 0){
        if(word_cnt == 2) {
        	int ranfromclient=atoi(message[1]);
        	int raninserver;
        	if(ranfromclient==-1){//client在logout時會將自己rannum設為1
        		strcpy(sendbuf,"Please login first.\n");
        		return;
        	}
        	else{//找此ran對印的名字
        		whoami(message,sendbuf);       	
	        	return;
        	}
        	

        }
        else {
        	strcpy(sendbuf,"Usage: whoami\n");
        	return;
        } 
    }
    else if(strncmp(message[0], "list-user", 9) == 0){
        if(word_cnt == 1) {
        	userList(message,sendbuf);
        	return ;
        }
        else {
        	strcpy(sendbuf,"Usage: list-user\n");
        	return;
        } 
    }
    else if(strncmp(message[0], "exit", 4) == 0){
        if(word_cnt == 1) {
        	strcpy(sendbuf,"end\n");
        	return ;
        }
        else return ;
    }
    else return ;
}

void user_register(char **receive, char *send){
	
	char name[100],email[100],password[500];
	strcpy(name,receive[1]);
	strcpy(email,receive[2]);
	strcpy(password,receive[3]);
	sprintf(send,"name:%s, email:%s, password:%s \n",name,email,password);
	
	//open db
	sqlite3 *db;
	int rc;
    char sql[500];
    char *zErrMsg = 0;
    sqlite3_stmt * stmt;

    rc = sqlite3_open("store.db", &db);
    if( rc==1 ) {
      fprintf(stderr, "Can't open database: %s\n", sqlite3_errmsg(db));
      return;
    }
          /*用prepare step馬上得知有沒有此名字*/
	sprintf(sql,"select * from USERS where Username ='%s'",name);
	sqlite3_prepare(db,sql,-1,&stmt,NULL);
	if(sqlite3_step(stmt) == SQLITE_ROW)//有此user
	{
		strcpy(send,"Username is already used.\n");
		sqlite3_finalize(stmt);

	}
	else////無此user加入db
	{
		sqlite3_finalize(stmt);
		sprintf(sql,"INSERT INTO USERS (Username,Email,Password,RanNum) "  \
		"VALUES ('%s', '%s', '%s',-1);",name,email,password);
		rc = sqlite3_exec(db, sql, callback, 0, &zErrMsg);
   
		if( rc != SQLITE_OK ){
		  	fprintf(stderr, "SQL error: %s\n", zErrMsg);
		  	sqlite3_free(zErrMsg);
		} 
		else {
		  	strcpy(send,"Register successfully.\n");
		}
		sqlite3_close(db);

	}

   		sqlite3_close(db);
   	
	return;
}

int user_login(char **receive, char *send, char *returnName){
	char name[100],password[500];
	char dbname[100],dbpassword[500];
	strcpy(name,receive[1]);
	strcpy(password,receive[2]);
	sprintf(send,"name:%s,  password:%s \n",name,password);
	
	//open db
	sqlite3 *db;
	int rc;
    char sql[500];
    char *zErrMsg = 0;
    sqlite3_stmt * stmt;

    rc = sqlite3_open("store.db", &db);
    if( rc==1 ) {
      fprintf(stderr, "Can't open database: %s\n", sqlite3_errmsg(db));
      return 0;
    }
          /*用prepare step馬上得知有沒有此名字*/
	sprintf(sql,"select * from USERS where Username ='%s'",name);
	sqlite3_prepare(db,sql,-1,&stmt,NULL);
	if(sqlite3_step(stmt) == SQLITE_ROW)//有此user
	{
		strcpy(dbname,(const char *)sqlite3_column_text(stmt,1));
		strcpy(dbpassword,(const char *)sqlite3_column_text(stmt,3));
		if(strcmp(dbname,name) == 0 && strcmp(dbpassword,password)==0){
			//找list中是否有記錄過此user login
			//沒找到給一ran num
			sqlite3_finalize(stmt);
			int i;
			srand( time(NULL) );
			int ranNum = rand();
			sprintf(sql,"UPDATE USERS set RanNum = %d where Username ='%s'", ranNum, name);
			sqlite3_prepare(db,sql,-1,&stmt,NULL);
			//回傳現在的child中login 的名字
			strcpy(returnName,name);
			sqlite3_step(stmt);
			sprintf(send,"Welcome, %s. %d\n", name,ranNum);//send給client
			sqlite3_finalize(stmt);
   			sqlite3_close(db);
   			return 1;
		}
		else{
			strcpy(send,"Login failed.\n");
			sqlite3_finalize(stmt);
   			sqlite3_close(db);
			return 0;
		}
	}
	else//無此user
	{
		strcpy(send,"Login failed.\n");
		sqlite3_finalize(stmt);
		sqlite3_close(db);
		return 0;
	}
}
int user_logout(char **receive, char *send,char *name){
	//open db
	sqlite3 *db;
	int rc;
    char sql[500];
    char *zErrMsg = 0;
    sqlite3_stmt * stmt;

    rc = sqlite3_open("store.db", &db);
    if( rc==1 ) {
      fprintf(stderr, "Can't open database: %s\n", sqlite3_errmsg(db));
      return 1;
    }
    sqlite3_prepare(db,sql,-1,&stmt,NULL);
	sprintf(sql,"UPDATE USERS set RanNum = -1 where Username ='%s'",name);
	sqlite3_step(stmt);
	sqlite3_finalize(stmt);
	sqlite3_close(db);
	sprintf(send,"Bye, %s.\n",name);
	return 0;
}
void whoami(char **receive, char *send){
	//open db
	sqlite3 *db;
	int rc;
    char sql[500];
    char *zErrMsg = 0;
    sqlite3_stmt * stmt;

    rc = sqlite3_open("store.db", &db);
    if( rc==1 ) {
      fprintf(stderr, "Can't open database: %s\n", sqlite3_errmsg(db));
      return;
    }
	sprintf(sql,"select Username from USERS where RanNum ='%d'",atoi(receive[1]));
	sqlite3_prepare(db,sql,-1,&stmt,NULL);
	sqlite3_step(stmt);
	strcpy(send,(const char *)sqlite3_column_text(stmt,0));
	strcat(send,"\n");
	sqlite3_finalize(stmt);
	sqlite3_close(db);
	return;

}

void userList(char **receive, char *send){
	//open db
	sqlite3 *db;
	int rc;
    char *sql;
    char *zErrMsg = 0;
    sqlite3_stmt * stmt;
    char all_string[5000];

    rc = sqlite3_open("store.db", &db);
    if( rc==1 ) {
      fprintf(stderr, "Can't open database: %s\n", sqlite3_errmsg(db));
      return;
    }
    strcpy(all_string, "Name\t\tEmail\n");
    sql="SELECT Username, Email from USERS ";
	rc = sqlite3_exec(db, sql, callback, (void*)all_string, &zErrMsg);
	if( rc != SQLITE_OK ){
	  	fprintf(stderr, "SQL error: %s\n", zErrMsg);
	  	sqlite3_free(zErrMsg);
	} 
	else {
	  	strcpy(send,all_string);
	}
	sqlite3_close(db);
}

static int callback(void *data, int argc, char **argv, char **azColName) {
	char tempStr[100];
   	int i;
   	for(i = 0; i<argc; i++){
      	sprintf(tempStr,"%-16s", argv[i] ? argv[i] : "NULL");
      	strcat(data, tempStr);
   	}
   	strcat(data, "\n");
   	return 0;
}

void createDB() {
   sqlite3 *db;
   char *zErrMsg = 0;
   int rc;
   char* sql;

   rc = sqlite3_open("store.db", &db);

   if( rc==1 ) {
      fprintf(stderr, "Can't open database: %s\n", sqlite3_errmsg(db));
      return;
   } else {
      fprintf(stderr, "Opened database successfully\n");
   }
     /* Create SQL statement */
   sql = "CREATE TABLE IF NOT EXISTS USERS("  \
      "UID INTEGER PRIMARY KEY AUTOINCREMENT,"\
      "Username TEXT NOT NULL UNIQUE,"\
      "Email TEXT NOT NULL,"\
      "Password TEXT NOT NULL,"\
      "RanNum INTEGER NOT NULL);";
      //"INSERT INTO USERS (Username,Email,Password) "  \
      //"VALUES ('Mark', '870313amy@gmil.com', 'matcha1314');";
      /* Execute SQL statement */
   rc = sqlite3_exec(db, sql, callback, 0, &zErrMsg);
   
   if( rc != SQLITE_OK ){
      fprintf(stderr, "SQL error: %s\n", zErrMsg);
      sqlite3_free(zErrMsg);
   } else {
      fprintf(stdout, "Table created successfully\n");
   }
   sqlite3_close(db);
}


