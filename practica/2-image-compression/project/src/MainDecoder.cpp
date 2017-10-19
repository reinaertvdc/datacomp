
#include <iostream>
#include <cstring>
#include "Init.h"
#include "RawFileParser.h"

int main(int argc, char *const argv[]) {
    std::cout << "DECODER" << std::endl << std::endl;
    Init init(argc, argv, true, false, true);
    if (!init.isInitialized()) {
        return 1;
    }

    ValueBlock4x4 blockList[init.getConfig().getHeight()/4][init.getConfig().getWidth()/4];

    // inverse DCT transform
    for (int i = 0; i < init.getConfig().getHeight() / 4; i++) {
        for (int j = 0; j < init.getConfig().getWidth() / 4; j++) {
            ValueBlock4x4 tmp(&init.getTmpEncodedImage()[(i*init.getConfig().getWidth()/4+j)*16]);
            tmp.deQuantize(init.getQuantMatrix());
            tmp.applyInverseDct();
            blockList[i][j] = tmp;
        }
    }

    //TODO: remove temporary save
    RawFileParser::writeFile8bit(init.getConfig().getDecodedFilePath(), &blockList[0][0],
                                 init.getConfig().getWidth(), init.getConfig().getHeight());
}