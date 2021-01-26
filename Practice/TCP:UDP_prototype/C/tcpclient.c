// TCP Client program 
#include <netinet/in.h> 
#include <stdio.h> 
#include <stdlib.h> 
#include <string.h> 
#include <sys/socket.h> 
#include <sys/types.h> 
#define PORT 5000 
#define MAXLINE 1024 
int main() 
{ 
	int sockfd; 
	char sendbuffer[MAXLINE],recbuffer[MAXLINE]; 
	char* message = "Hello Server"; 
	struct sockaddr_in servaddr; 

	int n, len; 
	// Creating socket file descriptor 
	if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0) { 
		printf("socket creation failed"); 
		exit(0); 
	} 

	memset(&servaddr, 0, sizeof(servaddr)); 

	// Filling server information 
	servaddr.sin_family = AF_INET; 
	servaddr.sin_port = htons(PORT); 
	servaddr.sin_addr.s_addr = inet_addr("127.0.0.1"); 


	int connect_state=0;
	while(fgets(sendbuffer, sizeof(sendbuffer), stdin)){
		if(connect_state==0){
			if ((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0) { 
				printf("socket creation failed"); 
				exit(0); 
			}
			if (connect(sockfd, (struct sockaddr*)&servaddr,sizeof(servaddr)) < 0) { 
				printf("\n Error : Connect Failed \n"); 
			} 
			else printf("connceted!!\n");
		}
		send(sockfd, sendbuffer, sizeof(sendbuffer),0); 
		connect_state=recv(sockfd, recbuffer, sizeof(recbuffer),0);
		if(connect_state!=0){
			printf("connect_state %d \nMessage from server: %s\n",connect_state,recbuffer);
		}
		 
		memset(sendbuffer, 0, sizeof(sendbuffer));
	}
	  
	
	
 
	close(sockfd); 
} 
