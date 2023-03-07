# JSON format guide

# |< marks the start of a branch that connects
# to the stations before it - prefix
# |> marks a branch connecting after - prefix
# || marks the last station of a branch - prefix
# ||> and ||< combine the above - prefix

# The station that connects to the mainline is the station
# closest to the connecting station <first >last

# >> means that the station can only be reached from
# the previous (one way path) - suffix
# << is the reverse - suffix

# load lines
import json
file = open("lines.json","r")
lines = json.load(file)
file.close()
linenames = list(lines.keys())

# start and destination input
start = input("Enter a starting station: ")
end = input("Enter the destination: ")




# returns 3 lists - the station a line is on, its index in the line, and every name the station has (eg bank and monument)
def find_station(station,walkway=False):
    found_lines = []
    found_index = []
    names = [station]
    for linename in linenames:
        line = lines[linename]
        for i in range(len(line)):
            if line[i].strip('|').strip('<').strip('>') == station:
                if 'Walkway' in linename and not walkway:
                    names = line
                    for otherstation in line:
                        if otherstation != station:
                            newlinenames, newlineindex,a = find_station(otherstation,walkway=True)
                            found_lines.extend(newlinenames)
                            found_index.extend(newlineindex)
                elif 'Walkway' not in linename:
                    found_lines.append(linename)
                    found_index.append(i)
    return found_lines, found_index,names



# returns a dictionary of which stations can be reached on one train - requires the three lists generated above
def onetrain(lines,indexes, names):
    pass




startlines, startindex, startnames = find_station(start)
print(f'{startnames} is on these lines: {startlines} in these places: {startindex}')

endlines, endindex, endnames = find_station(end)
print(f'{endnames} is on these lines: {endlines} in these places: {endindex}')