#include <iostream>
#include "miotapi.cpp"

main(){
    std::cout << "Using Miot version " << Miot::VERSION << "\n";

    auto api = Miot::API("your access token");

    std::cout << "API accessibility status: " << api.status() << std::endl;

    auto res = std::string(api.getUsers({{"uuid", "u/mrybs"}})[0]);
    std::cout << res << std::endl;
}