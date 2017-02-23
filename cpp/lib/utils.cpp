#include <cstdio>
#include "area.hpp"
#include "BearLibTerminal.h"
#include <iostream>
#include <memory>
#include <cmath>
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

std::vector<color_t> fade_colors(color_t a, color_t b, int steps)
{
    std::unique_ptr<color_t> current = &a;
    std::unique_ptr<color_t> color2 = &b;
    
    int step_a = abs(current[0] - color2[0]) / steps;
    int step_r = abs(current[1] - color2[1]) / steps;
    int step_g = abs(current[2] - color2[2]) / steps;
    int step_b = abs(current[3] - color2[3]) / steps;

    vector<color_t> vec();
    while (vec.back() != b)
    {
	vec.push_back(*current);

	/* alpha channel */
	if (current[0] < color2[0])
	{
	    current[0] -= step_a;
	}
	else if (current[0] > color2[0])
	{
	    current[0] += step_a;
	}

	/* red channel */
	if (current[1] < color2[1])
	{
	    current[1] -= step_r;
	}
	else if (current[1] > color2[1])
	{
	    current[1] += step_r;
	}

        /* green channel */
	if (current[2] < color2[2])
	{
	    current[2] -= step_g;
	}
	else if (current[2] > color2[2])
	{
	    current[2] += step_g;
	}

	/* blue channel */
	if (current[3] < color2[3])
	{
	    current[3] -= step_b;
	}
	else if (current[3] > color2[3])
	{
	    current[3] += step_b;
	}
    }

    return vec;
}

std::string to_upper(std::string str)
{
    std::transform(str.begin(), str.end(), str.begin(), ::toupper);
    return str;
}

std::vector<std::string> split_string(const std::string& str,
				      const std::string& delimiter)
{
    std::vector<std::string> strings;
    std::string::size_type pos = 0;
    std::string::size_type prev = 0;
    while ((pos = str.find(delimiter, prev)) != std::string::npos)
    {
	strings.push_back(str.substr(prev, pos - prev));
	prev = pos + 1;
    }

    // To get the last substring (or only, if delimiter is not found)
    strings.push_back(str.substr(prev));
    return strings;
}

std::vector<area::Point> bresenham(area::Point start, area::Point end)
{
    std::vector<area::Point> line;
    double dx = end.x - start.x;
    double dy = end.x - start.y;
    double derr = abs(dy / dx);
    double err = 0;

    int y = start.y;
    for (int x=start.x; x <= end.x; x++)
    {
	line.push_back({x,y});
	err += derr;

	if (err >= 0.5)
	{
	    y++;
	    err -= 1.0;
	}
    }

    return line;
}
