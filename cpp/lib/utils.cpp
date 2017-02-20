#include <cstdio>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <sstream>
#include <vector>
#include <array>

std::string exec(const char* cmd) 
{
    std::array<char, 128> buffer;
    std::string result;
    std::shared_ptr<FILE> pipe(popen(cmd, "r"), pclose);
    if (!pipe) throw std::runtime_error("popen() failed!");
    while (!feof(pipe.get())) {
	if (fgets(buffer.data(), 128, pipe.get()) != NULL)
	{
	    result += buffer.data();
	}
    }
    return result;
}

template<typename Out>
void split(const std::string &s, char delim, Out result) {
    std::stringstream ss;
    ss.str(s);
    std::string item;
    while (std::getline(ss, item, delim)) {
        *(result++) = item;
    }
}

std::vector<std::string> split(const std::string &s, char delim) {
    std::vector<std::string> elems;
    split(s, delim, std::back_inserter(elems));
    return elems;
}

std::vector<color_t> fade_colors(color_t a, color_t b)
{
    color_t *current = &a;
    color_t *color2 = &b;

    vector<color_t> vec();
    while (vec.back() != b)
    {
	vec.push_back(*current);

	/* alpha channel */
	if (current[0] < color2[0])
	{
	    current[0]--;
	}
	else if (current[0] > color2[0])
	{
	    current[0]++;
	}

	/* red channel */
	if (current[1] < color2[1])
	{
	    current[1]--;
	}
	else if (current[1] > color2[1])
	{
	    current[1]++;
	}

        /* green channel */
	if (current[2] < color2[2])
	{
	    current[2]--;
	}
	else if (current[2] > color2[2])
	{
	    current[2]++;
	}

	/* blue channel */
	if (current[3] < color2[3])
	{
	    current[3]--;
	}
	else if (current[3] > color2[3])
	{
	    current[3]++;
	}
    }

    return vec;
}

std::string to_upper(std::string str)
{
    std::transform(str.begin(), str.end(), str.begin(), ::toupper);
    return str;
}
