
#include <iostream>
#include "Init.h"

int main(int argc, char *const argv[]) {
    std::cout << "CODEC" << std::endl << std::endl;
    Init init(argc, argv, true, true);
    if (!init.isInitialized()) {
        return 1;
    }
}
