cmake_minimum_required (VERSION 2.6)
project (konker)

add_executable(
konker
#add all .c/.cc files here, otherwise they wont be compiled and linked
src/main.cc
src/person.cc
src/inlezen.cc
)

#define a place where #include<..> can search from
include_directories(
   "include/"
   )

set_target_properties(konker PROPERTIES RUNTIME_OUTPUT_DIRECTORY "build/")
## set compiler settings here : 

#-Wall instructs g++ the show all compile warnings. There should be no compile warnings.
#-g causes the linker to link c++ code with the machinecode, such that e.g. valgrind can give directed messeges towards your code, which is nice :)

add_definitions("-Wall -g -O2 -c")   

#link the std math library to the program
target_link_libraries( konker
   -lm
)
