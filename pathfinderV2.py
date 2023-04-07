# JSON format guide

# |< marks the start of a branch that connects
# to the stations before it - prefix
# |> marks a branch connecting after - prefix
# || marks the last station of a branch - prefix
# ||> and ||< combine the above - prefix

# The station that connects to the mainline is the station
# closest to the connecting station <first >last

# strip the <|> symbols when showing to the user

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
                    else:
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
# specify line to get a specific route
def all_one_train_stations(onetrain, clean=True, line = ''):
    all_stations_lists = [check['all_stations'] for check in onetrain if ((check['line'] == line) or (line == ''))]
    all_stations = []
    [all_stations.extend(stats) for stats in all_stations_lists]
    all_stations = [station.strip('|').strip('<').strip('>') for station in all_stations[:]]
    return all_stations

# check if a given station is in the result of a onetrain() call
# returns True or False
# specify line to check a specific route
def is_station_on_one_train(onetrain, dest_names, clean=True, line = ''):
    stations = all_one_train_stations(onetrain, clean=clean, line=line)
    return any([name in stations for name in dest_names])
    

# why didn't I make this before!
def clean(station):
    return station.strip('|').strip('>').strip('<')


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
        clean_all_stations = [clean(station) for station in all_stations]
        if any([val in clean_all_stations for val in dest_names]):
            # first find the location(s) of dest_names on the whole line
            locations = []
            for i in range(len(lines[line['line']])):
                if clean(lines[line['line']][i]) in dest_names or lines[line['line']][i] in dest_names:
                    locations.append(i)
            # get the associated amounts of stations between
            between = [stations_between(line['index'], val, line['line']) for val in locations]
            for i in range(len(between)):
                found.append([line['line'], between[i]])
    return found




# returns a list of all termini of a station on a line
def find_termini(onetrain, line):
    termini = {}
    line_data = [val for val in onetrain if val['line'] == line][0]
    stations = lines[line]
    # backwards
    # if direction = |> just add the first station with |>
    # else add all previous stations with |> and index 0
    back = []
    for i in range(line_data['index'], -1, -1):
        if '|>' in stations[i]:
            back.append(clean(stations[i]))
            if line_data['direction'] == '|>':
                break
        if i == 0:
            back.append(clean(stations[i]))
    
    termini['back'] = back

    # forwards
    # if direction = |< just add the first ||
    # else if |< is found add the next ||, and the last station
    forward = []
    lookout = False
    for i in range(line_data['index'], len(stations)):
        if line_data['direction'] == '|<' and '||' in stations[i]:
            forward.append(clean(stations[i]))
            break

        if '|<' in stations[i]:
            lookout = True
        if '||' in stations[i] and lookout:
            forward.append(clean(stations[i]))
            lookout = False
        
        if i == len(stations) - 1:
            forward.append(clean(stations[i]))
    
    termini['forward'] = forward

    return termini
                                                                                                                                            

# checks if a station is between two others on a certain line
# this is done by:
# getting the single-train distance each way
# isolating the one line
# check if one is positive and one is negative (either can be 0)
def is_station_between(start_names, end_names, check_onetrain, line):
    check_to_start = get_to_station_one_train(check_onetrain, start_names)
    check_to_end = get_to_station_one_train(check_onetrain, end_names)
    start_distance = [val[1] for val in check_to_start if val[0] == line]
    end_distance = [val[1] for val in check_to_end if val[0] == line]

    between = False

    # as there could still be multiple values check every combination
    for start in start_distance:
        for end in end_distance:
            if (start <= 0 and end >= 0) or (start >= 0 and end <= 0):
                between = True
    
    return between




# returns specific termini for getting to a station
# possible is from find_termini(start_onetrain, line)
def termini_to_get_to(possible, start_names, end_onetrain, line):
    distance = [-val[1] for val in get_to_station_one_train(end_onetrain, start_names) if val[0] == line][0]
    if distance <= 0:
        matches = [val for val in possible['back'] if is_station_between(start_names, [val], end_onetrain, line)]
    else:
        matches = [val for val in possible['forward'] if is_station_between(start_names, [val], end_onetrain, line)]
    return matches


# find a path that takes two trains to get there
# output is list of [line, stations, towards, changeat, line2, stations2, towards2]
def two_train_path(start_onetrain, start_names, end_onetrain, end_names):
    matches = []

    # go through every station on every line ONCE EACH
    checked_stations = []
    for line in start_onetrain:
        for station in line['all_stations']:
            if clean(station) not in checked_stations:
                checked_stations.append(clean(station))

                # get information about that station
                mid_lines, mid_index, mid_names = find_station(clean(station))
                print(mid_names)
                mid_onetrain = onetrain(mid_lines, mid_index)

                # if from that station you can get to the destination
                if get_to_station_one_train(mid_onetrain, end_names) != []:
                    # celebrate as a match has been found
                    # find the possible routes for each leg
                    leg1_path = get_to_station_one_train(start_onetrain, mid_names)
                    leg2_path = get_to_station_one_train(mid_onetrain, end_names)

                    # piece together each possible combination of leg1 and leg2
                    for leg1 in leg1_path:
                        for leg2 in leg2_path:
                            leg1_line = leg1[0]
                            leg1_distance = leg1[1]
                            leg1_termini = termini_to_get_to(find_termini(start_onetrain, leg1_line), start_names, mid_onetrain, leg1_line)
                            
                            changeat = [name for name in mid_names if is_station_on_one_train(start_onetrain, [name], line = leg1_line)][0]
                            
                            leg2_line = leg2[0]
                            leg2_distance = leg2[1]
                            leg2_termini = termini_to_get_to(find_termini(mid_onetrain, leg2_line), mid_names, end_onetrain, leg2_line)

                            route = [leg1_line, leg1_distance, leg1_termini, changeat, leg2_line, leg2_distance, leg2_termini]
                            if route not in matches:
                                matches.append(route)

    return matches


# find a path that takes 3 trains - this is the maximum possible
# [line1, stations1, termini1, change1,
#  line2, stations2, termini2, change2,
#  line3, stations3, termini3, total_stations]
def three_train_path(start_onetrain, start_names, end_onetrain, end_names):
    matches = []

    # go through every station on every line ONCE EACH
    checked_stations = []
    for line in start_onetrain:
        for station in line['all_stations']:
            if clean(station) not in checked_stations:
                checked_stations.append(clean(station))

                # get information about that station
                mid_lines, mid_index, mid_names = find_station(clean(station))
                print(mid_names)
                mid_onetrain = onetrain(mid_lines, mid_index)

                # if from that station you can get to the destination
                leg2_path = two_train_path(mid_onetrain, mid_names, end_onetrain, end_names)
                if leg2_path != []:
                    # celebrate as a match has been found
                    # find the possible routes for each leg (this version already has leg2/3)
                    leg1_path = get_to_station_one_train(start_onetrain, mid_names)

                    # piece together each possible combination of leg1 and leg2
                    for leg1 in leg1_path:
                        for leg2 in leg2_path:
                            leg1_line = leg1[0]
                            leg1_distance = leg1[1]
                            leg1_termini = termini_to_get_to(find_termini(start_onetrain, leg1_line), start_names, mid_onetrain, leg1_line)
                            
                            changeat = [name for name in mid_names if is_station_on_one_train(start_onetrain, [name], line = leg1_line)][0]

                            route = [leg1_line, leg1_distance, leg1_termini, changeat]
                            route.extend(leg2)
                            if route not in matches:
                                matches.append(route)

    return matches




# get the length of the longest string in a list
# if none are longer than s just return s
def longest(l, s):
    longest_str = s
    for val in l:
        if len(str(val)) > longest_str:
            longest_str = len(str(val))
    return longest_str

# return a cleaned string of the list
def cleanlist(l):
    return str(l).replace('"', "'").replace('[\'', '').replace('\']', '').replace('\', \'', ' or ')

# returns a string with a given character added to become a certain length
def pad_string(string, length, char = ' '):
    space_r = ((length - len(string)) // 2) * char
    space_l = ((((length - len(string)) // 2) + ((length - len(string)) % 2))) * char
    return f'{space_l}{string}{space_r}'

# work out stuff
startlines, startindex, startnames = find_station(start)
start_onetrain = onetrain(startlines,startindex)
print(start_onetrain)
#print(f'{startnames} is on these lines: {startlines} in these places: {startindex}')

endlines, endindex, endnames = find_station(end)
end_onetrain = onetrain(endlines,endindex)
print(end_onetrain)
#print(f'{endnames} is on these lines: {endlines} in these places: {endindex}')

one_train_routes = get_to_station_one_train(start_onetrain, endnames)

#print(one_train_routes)

# if possible on a single train show the possible routes
if one_train_routes != []:
    # to make the table look nice
    longest_str = 0
    for route in one_train_routes:
        termini = termini_to_get_to(find_termini(start_onetrain, route[0]), startnames, end_onetrain, route[0])
        str_termini = cleanlist(termini)
        if len(str_termini) > longest_str:
            longest_str = len(str_termini)

    topbar = '_' * longest_str
    lowerbar = '‾' * (longest_str + 38)
    space_towards_r = ((longest_str - 5) // 2) * '_'
    space_towards_l = ((((longest_str - 5) // 2) + ((longest_str - 5) % 2))) * '_'

    print(f' ______________________________________{topbar}')
    print(f'|_________Line_________|__Stations__|{space_towards_l}Towards{space_towards_r}|')
    for route in one_train_routes:
        line = route[0]
        distance = str(abs(route[1]))
        #print(find_termini(start_onetrain, line))
        termini = termini_to_get_to(find_termini(start_onetrain, line), startnames, end_onetrain, line)
        str_termini = cleanlist(termini)

        space_line_r = ((22 - len(line)) // 2) * ' '
        space_line_l = ((((22 - len(line)) // 2) + ((20 - len(line)) % 2))) * ' '

        space_dist_r = ((12 - len(distance)) // 2) * ' '
        space_dist_l = (((12 - len(distance)) // 2) + ((12 - len(distance)) % 2)) * ' '

        space_towards_r = ((longest_str + 2 - len(str_termini)) // 2) * ' '
        space_towards_l = ((((longest_str + 2 - len(str_termini)) // 2) + ((longest_str + 2 - len(str_termini)) % 2))) * ' '

        print(f'|{space_line_l}{line}{space_line_r}|{space_dist_l}{distance}{space_dist_r}|{space_towards_l}{str_termini}{space_towards_r}|')
    print(f' {lowerbar}')


else:
    # two train logic
    two_trains = two_train_path(start_onetrain, startnames, end_onetrain, endnames)
    
    if two_trains != []:
        # get the longest of each string for table length
        longest_leg1_line = longest([val[0] for val in two_trains], 4)
        longest_leg1_termini = longest([cleanlist(val[2]) for val in two_trains], 7)
        longest_changeat = longest([val[3] for val in two_trains], 9)
        longest_leg2_line = longest([val[4] for val in two_trains], 4)
        longest_leg2_termini = longest([cleanlist(val[6]) for val in two_trains], 7)

        top_line_length = longest_leg1_line + longest_leg1_termini + longest_changeat + longest_leg2_line + longest_leg2_termini + 53

        print(' ' + ('_' * top_line_length))
        print('|_'+pad_string('Line', longest_leg1_line, '_')+'_|_Stations_|_'+pad_string('Towards', longest_leg1_termini, '_')\
            +'_|_'+pad_string('Change_At', longest_changeat, '_')+'_|_'+pad_string('Line', longest_leg2_line, '_')+'_|_Stations_|_'\
                +pad_string('Towards', longest_leg2_termini, '_')+'_|_Total_Stations_|')
        
        for route in two_trains:
            line1 = pad_string(route[0], longest_leg1_line)
            stations1 = pad_string(str(abs(route[1])), 8)
            termini1 = pad_string(cleanlist(route[2]), longest_leg1_termini)
            change = pad_string(route[3], longest_changeat)
            line2 = pad_string(route[4], longest_leg2_line)
            stations2 = pad_string(str(abs(route[5])), 8)
            termini2 = pad_string(cleanlist(route[6]), longest_leg2_termini)
            total_stations = pad_string(str(abs(route[1]) + abs(route[5])), 14)

            print(f'| {line1} | {stations1} | {termini1} | {change} | {line2} | {stations2} | {termini2} | {total_stations} |')

        print(' ' + ('‾' * top_line_length))

    else:
        # try 3 trains
        three_trains = three_train_path(start_onetrain, startnames, end_onetrain, endnames)

        if three_trains == []:
            print('Impossible in three trains or less')
        
        else:
            print()
            print(len(three_trains), 'matches found.') 
            for i in range(len(three_trains)):
                print('______________________________________________')
                print('Option', str(i+1) + ':')
                route = three_trains[i]
                
                line1 = route[0]
                stations1 = str(abs(route[1]))
                termini1 = cleanlist(route[2])
                change1 = route[3]
                line2 = route[4]
                stations2 = str(abs(route[5]))
                termini2 = cleanlist(route[6])
                change2 = route[7]
                line3 = route[8]
                stations3 = str(abs(route[9]))
                termini3 = cleanlist(route[10])
                total_stations = str(int(stations1) + int(stations2) + int(stations3))

                print(f'''Start on line: {line1}
Go for stations: {stations1}
Towards: {termini1}
Get off at: {change1}
Change onto line: {line2}
Go for stations: {stations2}
Towards: {termini2}
Get off at: {change2}
Change onto line: {line3}
Go for stations: {stations3}
Towards: {termini3}
Total stations {total_stations}
‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾''')
                if i == len(three_trains) - 1:
                    input('Press Enter for the next one')