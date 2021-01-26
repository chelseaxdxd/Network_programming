#include <stdio.h> 
#include <stdlib.h> 
#include <unistd.h> 
#include <string.h> 
#include <sys/types.h> 
#include <sys/socket.h> 
#include <arpa/inet.h> 
#include <netinet/in.h> 
#include <stdbool.h>

#define BUF_SIZE 1024 
int ranNum=-1;
  
int check_format(char *sendbuf); 
int main(int argc, char *argv[]) { 
    char sendbuf[BUF_SIZE],recvbuf[BUF_SIZE];//傳話的字串
    int sockfd_UDP = 0;//socket描述符
    int sockfd_TCP = 0;
    struct sockaddr_in serverinfo; 
    
    //設定執行client之格式為./client host port  ex ./client 127.0.0.1 7890 
    if (argc < 2) {
    fprintf(stderr, "Usage: %s host port \n", argv[0]);//argv[0]為./client
    exit(EXIT_FAILURE);//關掉程式
    }
    
    //建立socket file descriptor
    sockfd_UDP = socket(AF_INET , SOCK_DGRAM , 0);//AF_INET為IPV4 SOCK_DGRAM為UDP 0為自動判定連線種類
    sockfd_TCP = socket(AF_INET , SOCK_STREAM , 0);
    if (sockfd_UDP == -1){
        perror("Fail to create a UDP socket.");
        exit(EXIT_FAILURE);
    }
    else if(sockfd_TCP == -1){
        perror("Fail to create a TCP socket.");
        exit(EXIT_FAILURE);
    }

    //sockaddr_in 設定serverinfo
    memset(&serverinfo, 0, sizeof(serverinfo)); //先將info歸空 bzero(&info,sizeof(info));也可 
    serverinfo.sin_family = AF_INET; 
    serverinfo.sin_port = htons(atoi(argv[2])); 
    serverinfo.sin_addr.s_addr = inet_addr(argv[1]);//NADDR_ANY;

    


    //字串處理部分  
    printf("********************************\n** Welcome to the BBS server. **\n********************************\n");
    int n, addrlen; 
    addrlen = sizeof(serverinfo);
    int TCP_conncet_sta = 0;//前面連過了
    while (1){
        printf("%% ");
        memset(sendbuf, 0, sizeof(sendbuf));
        memset(recvbuf, 0, sizeof(recvbuf));
        fgets(sendbuf, sizeof(sendbuf), stdin);
        int format=2;
        format=check_format(sendbuf);
        if(format==1){//UDP

            sendto(sockfd_UDP, sendbuf, BUF_SIZE,0, (const struct sockaddr *) &serverinfo, sizeof(serverinfo)); 
            n = recvfrom(sockfd_UDP, (char *)recvbuf, BUF_SIZE,0, (struct sockaddr *) &serverinfo, (socklen_t*)&addrlen); 
            recvbuf[n] = '\0';
            printf("%s", recvbuf); 
        }
        else if(format==2){ //TCP
            
            if(TCP_conncet_sta == 0){ //TCP reconnect
                if ((sockfd_TCP = socket(AF_INET, SOCK_STREAM, 0)) < 0) { 
                    printf("socket creation failed"); 
                    exit(0); 
                }
                if (connect(sockfd_TCP, (struct sockaddr*)&serverinfo, sizeof(serverinfo)) < 0) { 
                printf("\n Error : Connect Failed \n"); 
                }
            }
            
            write(sockfd_TCP, sendbuf, sizeof(sendbuf));  
            TCP_conncet_sta = read(sockfd_TCP, recvbuf, sizeof(recvbuf));
            if(TCP_conncet_sta!=0){
                char string[BUF_SIZE];
                strcpy(string,recvbuf);
                char * token = strtok(string, " ");
                char* message[4];
                int i=0;
                if(strncmp(token, "Welcome,", 8) == 0){
                    while( token != NULL ) {
                        message[i] = token;
                        i++;
                        token = strtok(NULL, " ");
                    }
                    printf("%s %s\n",message[0],message[1]);
                    ranNum=atoi(message[2]);  
                }
                else if(strncmp(token,"end",3)==0) {
                    close(sockfd_TCP);
                    close(sockfd_UDP);
                    exit(EXIT_SUCCESS);
                }
                else printf("%s", recvbuf);     
            } 

        }
        else continue;
        
    }
    close(sockfd_UDP); 
    close(sockfd_TCP); 
    return 0; 
} 
int check_format(char *sendbuf){
    char string[500];
    strcpy(string,sendbuf);
    char * token = strtok(string, " ");
    char* message[4];
    int i=0, word_cnt=0;
    while( token != NULL ) {
        message[i] = token;
        i++; word_cnt++;
        token = strtok(NULL, " ");
    }
    if(strncmp(message[0], "register", 8) == 0){
        return 1;//UDP
    }
    else if(strncmp(message[0], "whoami", 6) == 0){
        sprintf(sendbuf,"whoami %d\n",ranNum);
        return 1;//UDP
    }
    else if(strncmp(message[0], "login", 5) == 0){
        return 2;//TCP
    }
    else if(strncmp(message[0], "logout", 6) == 0){
        ranNum=-1;
        return 2;//TCP
    }
    else if(strncmp(message[0], "list-user", 9) == 0){
        return 2;//TCP
    }
    else if(strncmp(message[0], "exit", 4) == 0){
        return 2;//TCP
    }
    else {
        printf("not in correct format\n");
        return 0;//none
    }
}
