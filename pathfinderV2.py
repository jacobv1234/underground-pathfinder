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



# returns a dictionary of which stations can be reached on one train - requires the first two of the three lists generated above
def onetrain(on_lines,indexes):
    stations = {}
    # iterate through every line in on_lines
    for i in range(len(on_lines)):
        on_line = on_lines[i]
        line = lines[on_line]
        index = indexes[i]
        # find if the station is on a branch by checking forwards to find || before |> or |<
        # whether or not it is on a branch affects future logic
        onbranch = False
        for j in range(index, len(line)):
            if '||' in line[j]:
                onbranch = True
                break
            elif ('|<' in line[j] or '|>' in line[j]) and j != index:
                break
        
        direction = ''
        if onbranch:
            # iterate backwards to find the associated |< or |>
            for j in range(index,0,-1):
                if '|<' in line[j]:
                    direction = '|<'
                    break
                if '|>' in line[j]:
                    direction = '|>'
                    break


    return stations





startlines, startindex, startnames = find_station(start)
print(f'{startnames} is on these lines: {startlines} in these places: {startindex}')

endlines, endindex, endnames = find_station(end)
print(f'{endnames} is on these lines: {endlines} in these places: {endindex}')

print(onetrain(startlines,startindex))

