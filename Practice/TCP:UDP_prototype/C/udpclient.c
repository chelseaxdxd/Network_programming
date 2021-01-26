// UDP client program 
#include <arpa/inet.h> 
#include <netinet/in.h> 
#include <stdio.h> 
#include <stdlib.h> 
#include <strings.h> 
#include <sys/socket.h> 
#include <sys/types.h> 
#define PORT 5000 
#define MAXLINE 1024 
int main() 
{ 
	int sockfd; 
	char sendbuffer[MAXLINE],recbuffer[MAXLINE]; ; 
	struct sockaddr_in servaddr; 

	int n, len; 
	// Creating socket file descriptor 
	if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) { 
		printf("socket creation failed"); 
		exit(0); 
	} 

	memset(&servaddr, 0, sizeof(servaddr)); 

	// Filling server information 
	servaddr.sin_family = AF_INET; 
	servaddr.sin_port = htons(PORT); 
	servaddr.sin_addr.s_addr = inet_addr("127.0.0.1"); 
	while(1){
	// send hello message to server
	fgets(sendbuffer, sizeof(sendbuffer), stdin); 
	sendto(sockfd, (const char*)sendbuffer, strlen(sendbuffer), 
		0, (const struct sockaddr*)&servaddr, 
		sizeof(servaddr)); 

	// receive server's response 
	printf("Message from server: "); 
	n = recvfrom(sockfd, (char*)recbuffer, MAXLINE, 
				0, (struct sockaddr*)&servaddr, 
				&len); 
	puts(recbuffer); 
	}
	close(sockfd); 
	return 0; 
} 
