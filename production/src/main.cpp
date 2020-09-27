#include <iostream>
#include <string>
#include "AlertSystem/twillio.h"

std::string getEnvVar( std::string const & key )
{
    char * val = getenv( key.c_str() );
    return val == NULL ? std::string("") : std::string(val);
}

int main() {
	std::string account_sid = getEnvVar("ACCOUNTSID");
	std::string auth_token = getEnvVar("AUTHTOKEN");

	std::string response;
	twilio::Twilio *twilio = new twilio::Twilio(account_sid, auth_token);

	printf("hello there");
	return 0;

}
