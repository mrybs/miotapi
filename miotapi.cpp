#pragma once

#include <string>
#include <list>
#include <curl/curl.h>
#include <iostream>
#include "json.hpp"

namespace Miot{
    static const char* VERSION = "0.1.2";

    class User{
        const void* api;
        const nlohmann::json& data;

    public:
        const std::string uuid;
        const int telegram_id;
        const std::string telegram_username;
        const std::string name;
        const std::vector<std::string>& flags;
        const std::string registration_date;


        User(const void* api, const nlohmann::json& data)
            :api(api), data(data), 
            uuid(std::string(data["uuid"])),
            telegram_id(data["telegram_id"]),
            telegram_username(data.contains("telegram_username") ? std::string(data["telegram_username"]) : nullptr),
            name(std::string(data["name"])),
            flags(data["flags"]),
            registration_date(std::string(data["registration_date"])){}

        operator std::string() const{
            std::stringbuf buffer;
            std::ostream stream(&buffer);
            stream << "User " << uuid;
            stream << "\nName: " << telegram_id;
            stream << "\nTelegram ID: " << telegram_id;
            stream << "\nTelegram username: @" << telegram_username;
            stream << "\nRegistration date: " << registration_date;
            return buffer.str();
        }
    };

    class API{
        const char* host;
        const char* protocol;
        const char* prefix;
        const unsigned long timeout;
        CURL* curl;
    
    protected:
        inline static size_t writeCallback(void* contents, size_t size, size_t nmemb, void* userp) {
            ((std::string*)userp)->append((char*)contents, size * nmemb);
            return size * nmemb;
        }

    private:
        static std::string makeHexByChar(char Char){
            std::stringstream buffer;
            buffer << std::hex << int(Char);
            return buffer.str();
        }

    protected:
        static std::string URLEncode(const std::string& text){
            std::string encoded = std::string();
            for(char c: text){
                encoded += "%";
                if(makeHexByChar(c).size() == 8){
                encoded += makeHexByChar(c)[6];
                encoded += makeHexByChar(c)[7];
                }else
                encoded += makeHexByChar(c);
            }
            return encoded;
        }
        
        static std::string jsonToGetArgs(nlohmann::json j){
            std::list<const char*> _args;
            for(const auto& el : j.items()){
                if(el.value() == nullptr) continue;
                std::cout << el.value() << std::endl;
                std::string arg;
                arg.reserve(el.key().size() + 1 + el.value().size());
                arg.append(el.key()).append("=").append(URLEncode(el.value()));
                _args.push_back(arg.c_str());
            }
            std::string args = "?";
            auto i = 0;
            for(const auto& arg : _args){
                args += arg;
                i++;
                if(i < _args.size()) args += '&';
            }
            return args;
        }

    public:
        API(const char* host, const char* protocol="https", const char* prefix="/api", const unsigned long timeout=1L)
            :host(host), protocol(protocol), prefix(prefix), timeout(timeout){
                curl_global_init(CURL_GLOBAL_DEFAULT);
                curl = curl_easy_init();
                if(!curl){
                    std::cout << "!curl" << std::endl;
                }
            }
        
        inline ~API() noexcept{
            curl_easy_cleanup(curl);
        }
    
    protected:
        nlohmann::json get(const char* meth, const unsigned char tries=3){
            std::string readBuffer;
            std::string url;
            url.reserve(strlen(protocol) + 3 + strlen(host) + strlen(prefix) + strlen(meth));
            url
                .append(protocol)
                .append("://")
                .append(host)
                .append(prefix)
                .append(meth);
            curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
            curl_easy_setopt(curl, CURLOPT_CONNECTTIMEOUT, timeout);
            curl_easy_setopt(curl, CURLOPT_TIMEOUT, timeout);
            curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, writeCallback);
            curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuffer);
            const auto res = curl_easy_perform(curl);
            if(res != CURLE_OK){
                if(tries > 1) return get(meth, tries - 1);
                std::cerr << "\n\n\u001b[31mcURL error: " << curl_easy_strerror(res) << "\u001b[0m" << std::endl;
                exit(2);
            }
            const auto result = nlohmann::json::parse(readBuffer);
            return result;
        }
    
    public:
        inline const char* status(){
            return std::string(get("/")["status"]).c_str();
        }

        std::vector<User> getUsers(const nlohmann::json& args){
            auto _users = get((std::string("/users") + jsonToGetArgs(args)).c_str());
            std::vector<User> users;
            for(const auto user : _users){
                users.push_back(User(this, nlohmann::json(user)));
            }
            return users;
        }
    };
}
