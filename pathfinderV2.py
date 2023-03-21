# JSON format guide

# |< marks the start of a branch that connects
# to the stations before it - prefix
# |> marks a branch connecting after - prefix
# || marks the last station of a branch - prefix
# ||> and ||< combine the above - prefix

# The station that connects to the mainline is the station
# closest to the connecting station <first >last


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
    stations = []
    # iterate through every line in on_lines
    for i in range(len(on_lines)):
        on_line = on_lines[i]
        line = lines[on_line]
        index = indexes[i]

        # find if the station is on a branch by checking forwards to find || before |> or |<
        # whether or not it is on a branch affects future logic
        onbranch = False
        for j in range(index, len(line)):
            if ('|<' in line[j] or '|>' in line[j]) and j != index:
                break
            elif '||' in line[j]:
                onbranch = True
                break
        
        direction = 'none'
        if onbranch:
            # iterate backwards to find the associated |< or |>
            for j in range(index,-1,-1):
                if '|<' in line[j]:
                    direction = '|<'
                    break
                if '|>' in line[j]:
                    direction = '|>'
                    break
        
        forward = []
        # iterate forwards to find all accessible stations
        for j in range(index,len(line)):
            station = line[j]
            if '|>' not in station:
                forward.append(station)
            if '||' in station and direction == '|<':
                break

            # branch logic
            if '|>' in station:
                offbranch = False
                while not offbranch:
                    if '||' in line[j]:
                        offbranch = True
                    j += 1
            
        back = []
        # iterate forwards to find all accessible stations
        for j in range(index,-1, -1):
            station = line[j]
            if '||' not in station:
                back.append(station)
            if '|>' in station and direction == '|>':
                break

            # branch logic
            if '||' in station:
                branch_stations = []
                for k in range(j,-1,-1):
                    branch_stations.append(line[k])
                    if '|<' in line[k]:
                        del branch_stations
                        break
                    elif '|>' in line[k]:
                        back.extend(branch_stations)
                        del branch_stations
                        break
        
        all_stations = forward[:]
        all_stations.extend(back)
        stations.append({
            'line' : on_line,
            'index' : index,
            'onbranch' : onbranch,
            'direction' : direction,
            'forward' : forward,
            'back' : back,
            'all_stations' : all_stations
        })

    return stations


# get the amount of stations between two indices
def stations_between(startindex, endindex, line):
    stations = lines[line]
    if startindex < endindex:
        distance = -1
        extra = 0
        while startindex + distance + extra != endindex:
            distance += 1
            station = stations[startindex + distance + extra]
            # branch logic
            if '|>' in station:
                # skip to where the branch ends
                for i in range(startindex + distance + extra, len(stations)):
                    if '||' in stations[i]:
                        extra += i - startindex - distance
                        break
            elif '|<' in station:
                # skip unless destination is found
                for i in range(startindex + distance + extra, len(stations)):
                    if i == endindex:
                        distance = i - startindex - extra
                        break
                    if '||' in stations[i]:
                        extra = i - startindex - distance
                        break
        return distance
    elif endindex < startindex:
        return -stations_between(endindex, startindex, line)
    else:
        return 0


# check if a given station is in the list of dictionaries returned above
# returns a list of lists in [line, num_stations] format
# num_stations is negative if backwards
# not as a dictionary so the same line can appear multiple times
# destination should not have branch symbols included
def get_to_station(onetrain, destination):
    found = []

    # iterate through every line
    for line in onetrain:
        all_stations = line['all_stations']
        clean_all_stations = [station.strip('|').strip('>').strip('<') for station in all_stations]
        if destination in clean_all_stations:
            # first find the location(s) of destination on the whole line
            locations = []
            for i in range(len(lines[line['line']])):
                if lines[line['line']][i] == destination:
                    locations.append(i)
            # get the associated amounts of stations between
            between = [stations_between(line['index'], val, line['line']) for val in locations]
            for i in range(len(between)):
                found.append([line['line'], between[i]])
    return found



startlines, startindex, startnames = find_station(start)
start_onetrain = onetrain(startlines,startindex)
print(f'{startnames} is on these lines: {startlines} in these places: {startindex}')

endlines, endindex, endnames = find_station(end)
end_onetrain = onetrain(endlines,endindex)
print(f'{endnames} is on these lines: {endlines} in these places: {endindex}')

print(get_to_station(start_onetrain, end))