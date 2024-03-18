This demo file uses msquic.

If you use windows or linux there are prebuilt libraries here: https://github.com/microsoft/msquic/releases/tag/v2.3.5

For mac you need to build the library yourself.  You will need the c compiler and cmake.  From there:

1. git clone https://github.com/microsoft/msquic.git
2. git submodule update --init --recursive
3. mkdir build
4. cd build
5. cmake ..
6. cmake --build .
7. sudo cmake --install . 

I also found for macos, if you install powershell you can also build msquic via a following the directions above for step 1 and 2.  Then you finish by executing `build.ps1` from the scripts directory. 