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

# start and end input
start = input("Enter a starting station: ")
end = input("Enter the end: ")




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
# the result of this is used to identify a station with many other functions
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
        # for loop is created manually so it bloody works
        j = index
        while j < len(line):
            station = line[j]
            if '|>' not in station or j == index:
                forward.append(station)
            if '||' in station and direction == '|<':
                break

            # branch logic
            if '|>' in station and j != index:
                offbranch = False
                while not offbranch:
                    if '||' in line[j]:
                        offbranch = True
                    j += 1
            j += 1
            
        back = []
        # iterate backwards to find all accessible stations
        # for loop is created manually so it bloody works
        j = index
        while j > -1:
            station = line[j]
            if '||' not in station or j == index:
                back.append(station)
            if '|>' in station and direction == '|>':
                break

            # branch logic
            if '||' in station and j != index:
                branch_stations = []
                for k in range(j,-1,-1):
                    branch_stations.append(line[k])
                    if '|<' in line[k]:
                        j -= len(branch_stations) - 1
                        del branch_stations
                        break
                    elif '|>' in line[k]:
                        back.extend(branch_stations)
                        j -= len(branch_stations) - 1
                        del branch_stations
                        break
            j -= 1

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
    # backwards is easier to calculate
    if endindex < startindex:
        # pseudocode to help
        # distance = 0
        # iterate backwards with i through the list until i = endindex starting at startindex
            # if || is found:
                # iterate backwards with j until |< or |> is found
                # if endindex is somewhere between i and j
                    # ignore
                # else
                    # i = j - 1
            # else
                # distance - 1
        
        # implementation
        distance = 0
        for i in range(startindex, endindex, -1):
            station = stations[i]
            if '||' in station:
                for j in range(i, 0, -1):
                    check = stations[j]
                    if '|<' in check or '|>' in check:
                        break
                if endindex not in range(j,i+1):
                    i = j - 1
            else:
                distance -= 1
        return distance
    # forwards is just backwards but opposite
    elif startindex < endindex:
        return -stations_between(endindex, startindex, line)
    else:
        return 0

# get a single list of all stations reachable in a single train
# clean strips the |<> symbols
def all_one_train_stations(onetrain, clean=True):
    all_stations_lists = [line['all_stations'] for line in onetrain]
    all_stations = []
    [all_stations.extend(stats) for stats in all_stations_lists]
    all_stations = [station.strip('|').strip('<').strip('>') for station in all_stations[:]]
    return all_stations

# check if a given station is in the result of a onetrain() call
# returns True or False
def is_station_on_one_train(onetrain, dest_names, clean=True):
    stations = all_one_train_stations(onetrain, clean=clean)
    return any([name in stations for name in dest_names])
    



# get from one station to another (one train journey)
# returns a list of lists in [line, num_stations] format
# num_stations is negative if backwards
# not as a dictionary so the same line can appear multiple times
# dest_names should not have branch symbols included
# dest_names is a list of station names
# onetrain is the output of the onetrain() function
def get_to_station_one_train(onetrain, dest_names):
    found = []

    # iterate through every line
    for line in onetrain:
        all_stations = line['all_stations']
        clean_all_stations = [station.strip('|').strip('>').strip('<') for station in all_stations]
        if any([val in clean_all_stations for val in dest_names]):
            # first find the location(s) of dest_names on the whole line
            locations = []
            for i in range(len(lines[line['line']])):
                if lines[line['line']][i] in dest_names:
                    locations.append(i)
            # get the associated amounts of stations between
            between = [stations_between(line['index'], val, line['line']) for val in locations]
            for i in range(len(between)):
                found.append([line['line'], between[i]])
    return found


# why didn't I make this before!
def clean(station):
    return station.strip('|').strip('>').strip('<')


# returns a list of all termini of a station on a line
def find_termini(onetrain, line):
    termini = []
    line_data = [val for val in onetrain if val['line']][0]
    stations = lines[line]
    # backwards
    # if direction = |> just add the first station with |>
    # else add all previous stations with |> and index 0
    for i in range(line_data['index'], -1, -1):
        if '|>' in stations[i]:
            termini.append(clean(stations[i]))
            if line_data['direction'] == '|>':
                break
        if i == 0:
            termini.append(clean(stations[i]))

    # forwards
    # if direction = |< just add the first ||
    # else if |< is found add the next ||, and the last station
    lookout = False
    for i in range(line_data['index'], len(stations)):
        if line_data['direction'] == '|<' and '|<' in stations[i]:
            termini.append(clean(stations[i]))
            break

        if '|<' in stations[i]:
            lookout = True
        if '||' in stations[i] and lookout:
            termini.append(clean(stations[i]))
            lookout = False
        
        if i == len(stations) - 1:
            termini.append(clean(stations[i]))

    return termini


# checks if a station is between two others on a certain line
# this is done by:
# getting the single-train distance each way
# isolating the one line
# check if one is positive and one is negative
def is_station_between(start_names, end_names, check_onetrain, line):
    pass




# returns specific termini for getting to a station



# work out stuff
startlines, startindex, startnames = find_station(start)
start_onetrain = onetrain(startlines,startindex)
print(f'{startnames} is on these lines: {startlines} in these places: {startindex}')

endlines, endindex, endnames = find_station(end)
end_onetrain = onetrain(endlines,endindex)
print(f'{endnames} is on these lines: {endlines} in these places: {endindex}')

one_train_routes = get_to_station_one_train(start_onetrain, endnames)

print(one_train_routes)


print(find_termini(start_onetrain, input('Line for termini: ')))