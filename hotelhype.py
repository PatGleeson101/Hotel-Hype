#Copyright (c) 2018 Patrick Gleeson
#The following program is free to run, distribute, learn from and modify

#Hotel Hype
import time
import random as r
import ast
import math

'''Classes'''
class Hotel():
    def __init__(self, gamenum,employees=[],freerooms=[],occrooms=[],residents=[],bal=3000,level=1,xp=0,day=0,rooms=0,adverts={},advert_level=0,amenities=[]):
        #initialise variables from data/defaults
        self.employees = employees
        self.freerooms = freerooms
        self.occrooms = occrooms
        self.residents = residents
        self.bal = int(bal)
        self.level = int(level)
        self.xp = int(xp)
        self.day = int(day)
        self.rooms = int(rooms)
        self.adverts = ast.literal_eval(str(adverts))
        self.advert_level = int(advert_level)
        self.gamenum = int(gamenum)
        self.amenities = ast.literal_eval(str(amenities))
        #ast.literal_eval takes a string form of (in this case) a list, and returns it as an actual (in this case) list

    def savegame(self):
        #Step 1: open file (read), read info, & modify this game's line.
        #Step 2: open file (write), write in the modified data
        #Do for hotel, rooms, employees & residents
        
        #Hotel data
        with open('hotels.txt','r') as f:
            hotels_data = f.readlines()
            #this game's item in the list   is all the hotel's attributes as strings (using map function) joind by '_', and with a \n at the end
            hotels_data[self.gamenum] = '_'.join(list(map(str,[self.bal,self.level,self.xp,self.day,self.rooms,self.adverts,self.advert_level,self.amenities]))) + '\n'
        with open('hotels.txt','w') as f:
            for i in hotels_data:
                f.write(i)

        #Room data
        with open('rooms.txt','r') as f:
            rooms_data = f.readlines()
            #see hotel version, but this time the occupied and free rooms data is separated by an additional '&' so they can be distinguished later
            rooms_data[self.gamenum] = '&'.join(['#'.join([i.data() for i in self.freerooms]),'#'.join(i.data() for i in self.occrooms)]) + '\n'
        with open('rooms.txt','w') as f:
            for i in rooms_data:
                f.write(i)

        #Employee data
        with open('employees.txt','r') as f:
            employees_data = f.readlines()
            #see above, plus a '#' separating each employee's data
            employees_data[self.gamenum] = '#'.join([i.data() for i in self.employees]) + '\n'
        with open('employees.txt','w') as f:
            for i in employees_data:
                f.write(i)

        #Guest data
        with open('residents.txt','r') as f:
            residents_data = f.readlines()
            #see above, with a '#' separating each guest's data
            residents_data[self.gamenum] = '#'.join([i.data() for i in self.residents]) + '\n'
        with open('residents.txt','w') as f:
            for i in residents_data:
                f.write(i)

    def addxp(self,xp):
        #add xp
        self.xp += xp
        #check for level-up
        if self.xp >= self.level**2*10: #the amount of xp required at level 'n' is n squared times 10
            self.xp -= self.level**2*10
            self.level += 1
            hprint(' Your hotel levelled up! Level {}'.format(self.level))
        
class Person():
    def __init__(self):
        #Initialise random characteristics
        self.gender = r.choice(['male','female'])
        self.fname = r.choice(firstnames[self.gender])
        self.lname = r.choice(lastnames)
        self.age = r.randint(23,70)
        self.richness = r.randint(40,200)
        self.room = 0 #to be substituted for room object later
        self.preferences = r.sample(list(sorted(appliances)),3)
        self.days = 0

    def declare(self,gender,fname,lname,age,richness,room,preferences,days):
        #Non random attribute setting (for loading the game)
        self.gender = gender
        self.fname = fname
        self.lname = lname
        self.age = int(age)
        self.richness = int(richness)
        self.room = int(room)
        self.preferences = ast.literal_eval(preferences)
        self.days = int(days)
        
    def checkin(self,room):
        #set room to the room object and add self to residents
        self.room = room
        h.residents.append(self)
        #move room from 'free' to 'occupied':
        h.freerooms.remove(room)
        h.occrooms.append(room)
        room.resident = self.fname +' '+ self.lname
        hprint('\n {} {} checked in!'.format(self.fname,self.lname))
        #random number of days to stay:
        self.days = r.randint(1,15)

    def checkout(self):
        #remove self from hotel
        self.room.resident = 'none'
        h.residents.remove(self)
        #move room back to 'free'
        h.occrooms.remove(self.room)
        h.freerooms.append(self.room)
        #final checkout
        hprint('\n '+self.fname+' '+self.lname+' checked out!')
        del self

    def data(self):
        #returns data in the format a_b_c_d, used for storage. map converts variables to strings
        return '_'.join(list(map(str,[self.gender,self.fname,self.lname,self.age,self.richness,self.room.roomno,self.preferences,self.days])))

class Employee(Person):
    def __init__(self):
        #Initialise 'Person' Characteristics
        Person.__init__(self)
        #Additional rate, ability, job characteristics
        self.rate = r.randint(9,30)
        self.ability = r.randint(1,10)
        self.job = 'None'

    #Declare function (see Person)
    def declare(self,gender,fname,lname,age,richness,room,preferences,days,rate,ability,job):
        #super() gets the parent class (Person), used to run the already defined declare function
        super().declare(gender,fname,lname,age,richness,room,preferences,days)
        #Additional attributes
        self.rate = int(rate)
        self.ability = int(ability)
        self.job = job

    def data(self):
        #data function for storage
        return '_'.join(list(map(str,[self.gender,self.fname,self.lname,self.age,self.richness,self.room,self.preferences,self.days,self.rate,self.ability,self.job])))

    def dojob(self):
        ability = math.ceil(self.ability/2)
        #initialise money variables
        income = 0
        expense = self.rate*4
        #dirty rooms, dirtiest -> least dirty. [i for i in...i.dirty != 0] gets all rooms that are dirty. 'key = lambda x: x.dirty' defines that the list is sorted by x.dirty for all x in the list
        rdirt = sorted([i for i in h.freerooms+h.occrooms if i.dirty != 0],key = lambda x: x.dirty, reverse=True)
        
        #cleaner is a common job
        if self.job == 'Cleaner':
            #cleans a random amount (based on ability level) of rooms
            for x in r.sample(rdirt,min(len(rdirt),1+int(ability//2.5))):
                x.dirty = 0
                hprint('\n Room {} was cleaned!'.format(x.roomno))

        #amenity jobs
        elif self.job in [i[0] for i in amenities.values()]: #gets the job associated with each amenity
            #chance of people using an amenity based on the employee's ability level
            if r.randrange(100) <= self.ability*12:
                #works out the amenity name (for later use), based on the job
                for amenity,data in amenities.items():
                    if data[0] == self.job:
                        amenityname = amenity
                #random sample (size based on ability) uses the amenity
                for p in r.sample(h.residents,min(r.randint(1,ability),len(h.residents))):
                    hprint('\n {} {} used the {}!'.format(p.fname,p.lname,amenityname))
                    income += amenities[amenityname][2]
            
        return income,expense

class Room():

    def __init__(self,roomtype,roomno='x',level=1,xp=0,rate=10,appliances=[],resident='none',dirty=0):
        if roomno == 'x': #if roomno is default, i.e. this is a new room          
            self.roomno = h.rooms + 1
        else:
            self.roomno = int(roomno)
        self.roomtype = roomtype
        self.level = int(level)
        self.xp = int(xp)
        self.rate = roomtypes[roomtype][1]
        self.appliances = ast.literal_eval(str(appliances))
        self.resident = resident
        self.dirty = int(dirty)

    def data(self):
        #data function
        return '_'.join(list(map(str,[self.roomtype,self.roomno,self.level,self.xp,self.rate,self.appliances,self.resident, self.dirty])))

    def addxp(self,xp):
        #see Hotel version of this funciton for details
        self.xp += xp
        if self.xp >= self.level**2*10:
            self.xp -= self.level**2*10
            self.level += 1
            hprint('\n Room {} is now level {}!'.format(self.roomno,self.level))
        
'''Hard-coded Collections/Constants'''

firstnames = {'male':['Patrick','Simon','Jonathan','Luke','Max','Alex','Bill','Robert','Sam','Craig','Henry','Barry','Ben','Nathan','George','Damon','Damien','Dan','Kevin','Matthew'],
              'female':['Samantha','Patricia','Ella','Rosie','Marsha','Chiniqua','Rainelle','Brittney','Lupita','Leshana','Gloria','Santana','Laura','Jade','Bella','Maria','Josephina','Jessica','Georgia','Jane','Molly','Sharon','Paris','Elouise','Polly','Annie','Debora','Celine','Ruth','Harley']}

lastnames = ["O'Neil","Smith","Adams","Hiett","Oakley","Cox","Tait","Gibb","Zhang","McKenner","Trump","Graham","McBoatFace","Drew","Tan","Santiago","Ye","Chang","Akari","Putin","Obama","Rosenbelov","Spears"]

#appliance:cost
appliances = {'TV':50,'Fridge':100,'Microwave':80,'Toaster':40,'Washing Machine':100,'Dryer':80,'Dishwasher':70}

#roomtype:[cost,rate]
roomtypes = {'Standard':[1000,100],'Improved':[1500,150],'Deluxe':[2000,200]}

dirtlevels = ['spotlessly clean','clean','pretty clean','mostly clean','a bit dirty','dirty','quite dirty','very dirty','terribly dirty','horrifically dirty','global-biohazard-level dirty']

#amenity:[job name, amenity cost, rate per use]
amenities = {'Laundromat':['Launderer',800,40],'Gym':['Fitness Trainer',1000,45],'Buffet':['Chef',600,40],'Arcade':['GameMaster',1200,50],'Bar':['Bartender',2000,60],'Casino':['Corrupt Dealer',10000,200]}

#appliance:[duration,effectiveness, cost]
advertisements = {'Flyers':[30,2,100],'Radio':[30,5,200],'TV':[15,10,400],'Hotels Combined':[10,8,150],'Trivago':[20,8,400]}

'''General Functions'''
def hprint(string):
    #for every character in the string
    for i in list(str(string)):
        #print that character individually, on the same line
        print(i,end='')
        #add a slight pause at punctuation
        if i == ',':
            time.sleep(0.1)
        elif i in ['.','!','?']:
            time.sleep(0.2)
    #auto-newline function, like with print
    print('')

def getchoice(options):
    #get choice until choice is in options
    while 1:
        choice = input('> ')
        if choice in map(str,options):
            break
        else:
            hprint('Sorry, that is not an available option.')
    #return choice as an integer (this function is only intended for numeric options)
    return int(choice)

def getline(file,gamenum):
    with open(file,'r') as f:
        #parse through lines in file
        for index, line in enumerate(f):
            #return appropriate line
            if index == gamenum:
                return line.rstrip()
            
'''Game functions'''       
#main menu
def mainmenu():
    while 1:
        hprint('\nMain menu:\n 1) New game\n 2) Load save\n 3) Quit')
        #get user choice
        choice = getchoice([1,2,3])
        #list of code to run for each option
        options = ['newgame()','loadgame()','quit()']
        #execute respective code
        if choice == 3:
            hprint("\nLogging off...")
        exec(options[choice-1])

#New game
def newgame():
    hprint('New game selected.')

    #get used hotel names & amount of hotels. 
    with open('index.txt','r') as f:
        hnames = [i.rstrip() for i in f.readlines()]
        gamenum = len(hnames)

    #new hotel
    global h
    h = Hotel(gamenum)

    #Create tutorial/starting employees
    ep1 = Employee()
    ep1.declare('male','Phil','Hiett',23,100,0,"['TV']",0,11,10,'Receptionist')
    ep2 = Employee()
    ep2.job = 'Cleaner'
    h.employees.append(ep1)
    h.employees.append(ep2)
    
    #Create initial rooms
    for i in range(3):
        h.freerooms.append(Room('Standard'))
        h.rooms += 1
                    
    #Name hotel
    while 1:
        hname = input('\nName your hotel:\n> ')
        if hname == '':
            hprint('Your hotel must have a name')
        elif hname in hnames:
            hprint('Hotel name taken.')
        else:
            break

    #save hotel name to file
    with open('index.txt','a') as f:
        f.write(hname+'\n')
    
    #Create file lines for new hotel:
    for i in ['hotels.txt','rooms.txt','employees.txt','residents.txt']:
        with open(i,'a') as f:
            f.write('\n')

    #Save data
    h.savegame()
        
    #Start Gameplay
    hprint("Welcome to your new hotel! Let's start your first day.")
    play()

#Load save
def loadgame():
    global gamenum
    hprint('Load game selected.')
    
    #get existing hotels
    with open('index.txt','r') as f:
        hotels = [i.rstrip() for i in f.readlines()]
        hnum = len(hotels)
    if hnum == 0:
        #no games saved
        hprint('No saved games.')
    else:
        #select from current games
        hprint('Choose game:\n')
        for i in range(hnum):
            hprint(' {}) {}'.format(i+1,hotels[i]))
        hprint('\n {}) Back'.format(hnum+1))

        gamenum = getchoice(range(1,hnum+2)) - 1

        if gamenum == hnum:
            return
        else:
            hprint('Loading...')
            #Get room data
            freerooms = []
            occrooms = []
            #split free room data from occupied room data
            (freeroomsstring,occroomsstring) = getline('rooms.txt',gamenum).split('&')
            #creates lists containing room data. each item is a list, which contains the room's attirbute values
            freeroomsdata = [i.split('_') for i in freeroomsstring.split('#')]
            occroomsdata = [i.split('_') for i in occroomsstring.split('#')]
            #create rooms
            if freeroomsstring != '':
                for i in freeroomsdata:
                    # '*i turns the list i - [a,b,c] - into arguments for the function, func(a,b,c)
                    freerooms.append(Room(*i))
            if occroomsstring != '':
                for i in occroomsdata:
                    occrooms.append(Room(*i))

            #Get employee data
            employees = []
            for i in getline('employees.txt',gamenum).split('#'):
                e = Employee()
                e.declare(*(i.split('_')))
                employees.append(e) 

            #Get resident data
            residents = []
            if occroomsstring != '':
                for i in getline('residents.txt',gamenum).split('#'):
                    r = Person()
                    r.declare(*(i.split('_')))
                    residents.append(r)

            #convert residents' roomnumbers to previously created room objects
            rooms = {}
            for i in occrooms:
                rooms[i.roomno] = i

            for i in residents:
                i.room = rooms[i.room]

            #Get hotel data
            hoteldata = [gamenum,employees,freerooms,occrooms,residents] + getline('hotels.txt',gamenum).split('_')

            #Generate hotel
            global h
            h = Hotel(*hoteldata)
            
            #achknowledge game has loaded
            hprint('\nGame resumed: {}\n Level {}\n XP {}/{}\n Day {}\n Guests {}/{}\n ${}'
           .format(hotels[h.gamenum],h.level,h.xp,h.level**2*10,h.day,len(h.residents),h.rooms,h.bal))

            #resume gameplay
            play()

#Gameplay
def play():
    while 1:
        h.savegame()

        #daily variables
        income = 0
        expenses = 0
        people = []
        
        h.day += 1
        hprint('Day {}:'.format(h.day))

        #Regulate Current guests
        for i in h.residents:
            i.room.addxp(1)
            i.days -= 1
            h.addxp(1)
            #chance of increasing room's dirtiness
            if r.randrange(100) <= 70:
                i.room.dirty += 1
                #User notified about dirtiness if it gets too high
                if i.room.dirty >= 4:
                    hprint("\n {} {}'s room is dirty!".format(i.fname,i.lname))
            #checkout guests who have finished their stays
            if i.days == 0:
                i.checkout()

        #New guests
        #amount of available guests is based on hotel level & advertising
        for i in range(r.randrange(h.level+h.advert_level,2*(h.level+h.advert_level))):
            people.append(Person())
        #copy people to avoid modifying the list being iterated over
        for i in people[:]:
            if len(h.freerooms) == 0:
                #no available rooms. no point trying to check in guests
                break
            for a in h.freerooms:
                #Criteria for checking in
                if (len(set(a.appliances).intersection(set(i.preferences)))*10 + i.richness-a.dirty*10+a.level*10) >= a.rate:
                    people.remove(i)
                    i.checkin(a)
                    break

        #avoid memory leakage by deleting unneeded potential guests
        for i in people:
            del i

        #Employee jobs
        #list of jobs
        avjobs = set([x.job for x in h.employees])
        #check if hotel has amenities which don't have a respective employee
        for i in h.amenities:
            if not amenities[i][0] in avjobs:
                hprint("\n Your {} can't be used without employing a {}".format(i,amenities[i][0]))

        #for each employee, perform their job and update expenses/income
        for i in h.employees:
            plusincome, plusexpenses = i.dojob()
            income += plusincome
            expenses += plusexpenses

        #Update Advertising
        for ad in list(h.adverts):
            h.adverts[ad] -= 1 #h.adverts is a dictionary, {active advertisement: days remaining}
            if h.adverts[ad] == 0:
                hprint(' Your advertising via {} has run out.'.format(ad))
                h.advert_level -= advertisements[ad][1]
                del h.adverts[ad]

        #Income based on guests
        for i in h.residents:
            income += i.room.rate
            
        h.bal += income - expenses
        #Daily summary
        hprint("\nToday's summary:\n Residents: {}/{}\n Total Dirty Rooms: {}\n Income: ${}\n Expenses: ${}\n Total Balance: ${}"
               .format(len(h.residents),h.rooms,len([i for i in h.freerooms+h.occrooms if i.dirty != 0]),income,expenses,h.bal))
        

        #Generate available employees
        newworkers = []
        for q in range(r.randrange(4)):
            newworkers.append(Employee())

        #User actions
        while 1:
            print('\nHotel Menu:\n 1) View/Edit Rooms\n 2) View/Edit Employees\n 3) View/Edit Amenities\n 4) View/Edit Advertising\n 5) View Residents\n 6) Start next day\n 7) Save & Quit\n')
            options = [['View/Edit Rooms','roommenu()'],['View/Edit Employees','newworkers=employeemenu(newworkers)'],
                       ['View/Edit Amenities','amenitymenu()'],['View/Edit Advertising','advertisingmenu()'],
                       ['View Residents','guestmenu()'],['Next Day'],['Save and Quit']]

            choice = getchoice(range(1,8)) - 1
            
            hprint('{} selected.'.format(options[choice][0]))
            if choice == 5:
                break
            elif choice == 6:
                h.savegame()
                hprint('Saving...')
                #delete all hotel's objects to prevent memory leakeage
                for i in h.occrooms+h.freerooms+h.employees+h.residents:
                    del i
                #back to main menu
                return
            else:
                #do corresponding function from the list above
                exec(options[choice][1])


'''Hotel Menu options'''
def roommenu():
    while 1:
        roomnums = {}
        #Display occupied rooms
        hprint('\n Occupied rooms:')
        #sorts occupied rooms by room number (so the display is logical)
        h.occrooms.sort(key = lambda x: x.roomno)
        if h.occrooms == []:
            print('  No rooms are currently occupied.')
        else:
            for i in h.occrooms:
                hprint('  {0}) Room {0} - Level {1} - {2}'.format(i.roomno,i.level,i.resident))
                roomnums[i.roomno] = i

        #Display unoccupied rooms
        hprint('\n Unoccupied rooms:')
        #sort unoccupied rooms by room number to make display ordered
        h.freerooms.sort(key = lambda x: x.roomno)
        if h.freerooms == []:
            print('  All rooms are currently occupied.')
        else:
            for i in h.freerooms:
                hprint('  {0}) Room {0} - Level {1}'.format(i.roomno,i.level))
                roomnums[i.roomno] = i

        #Display other options
        #lenrooms is the amount of rooms, equivalent to the highest room number
        lenrooms = max(list(roomnums))
        hprint('\n {}) Buy new room'.format(lenrooms+1))
        hprint(' {}) Back to hotel menu'.format(lenrooms+2))
        hprint('Select a room to view/edit or choose another option:')
        
        #User input
        rnum = getchoice(range(1,lenrooms+3))
        
        if rnum in roomnums.keys():
            #User selected a room
            r = roomnums[rnum]
            while 1:
                #Display data
                hprint('\n Room {} ({}):'.format(rnum,r.roomtype))
                hprint('  Level: {}\n  XP: {}/{}\n  Rate: ${}/night\n  Guest: {}\n  This room is {}'
                       .format(r.level,r.xp,r.level**2*10,r.rate,r.resident,dirtlevels[r.dirty]))
                hprint('  Appliances:')
                if r.appliances == []:
                    hprint('  This room has no appliances.')
                else:
                    for appliance in r.appliances:
                        hprint('   '+appliance)
                
                #Display options
                hprint('\nOptions:')
                hprint(' 1) Add appliance\n 2) Back to room menu\n 3) Back to hotel menu')

                #User input
                choice = getchoice(['1','2','3'])
                    
                if choice == 1:
                    #New appliances
                    hprint('Available appliances:')
                    #available appliances are the difference between all appliances and the ones already owned
                    freeappliances = sorted(set(appliances.keys()).difference(set(r.appliances)))

                    #Display available appliances
                    if freeappliances == []:
                        hprint(' This room already has all the appliances.')
                    else:
                        p = len(freeappliances)
                        for x in range(p):
                            hprint(' {}) {} - ${}'.format(x+1,freeappliances[x],appliances[freeappliances[x]]))
                        hprint('\n {}) Back to room details'.format(p+1))
                        hprint('Select option:')
                        
                        apchoice = getchoice(range(1,p+2))

                        if apchoice in range(1,p+1):
                            #User tried to buy an appliance
                            cost = appliances[freeappliances[apchoice-1]]
                            if h.bal >= cost:
                                #They have enough money
                                hprint('You bought a {} for room {}'.format(freeappliances[apchoice-1],rnum))
                                h.bal -= cost
                                r.appliances.append(freeappliances[apchoice-1])
                                r.addxp(30)
                                h.addxp(10)
                            else:
                                #They are too poor
                                hprint("You don't have enough funds")
                        else:
                            #User chose the 'back' option
                            break
                    
                #Other options 
                elif choice == 2:
                    #Back to room menu
                    break
                elif choice == 3:
                    #Back to hotel menu
                    return

        #first choice wasn't a room number
        elif rnum == lenrooms+1:
            #buying a room
            hprint('Buy new room:')
            #get list of all room types (roomtypes dictionary keys) sorted by their nightly rate (roomtypes[x][1])
            rooms = sorted(list(roomtypes),key = lambda x: roomtypes[x][1])
            roomslen = len(rooms)
            
            #Display room options
            for i in range(roomslen):
                room = rooms[i]
                hprint(' {}) {} - ${}/night - ${}'.format(i+1,room,roomtypes[room][1],roomtypes[room][0]))
            hprint('\n {}) Back to room menu'.format(roomslen+1))

            #User input (again)
            choice = getchoice(range(1,roomslen+2))
            
            if choice in range(1,roomslen+1):
                #User wants to buy a room
                room = rooms[choice-1]
                cost = roomtypes[room][0]
                if h.bal >= cost:
                    #They have enough money
                    h.freerooms.append(Room(room, h.rooms+1))
                    h.bal -= cost
                    h.addxp(30)
                    h.rooms += 1
                    hprint('New {} room constructed.'.format(room))
                else:
                    #They don't have enough money
                    hprint("You don't have enough funds to buy this room")
            #No need for an else/elif, as the other option is 'back to rooms', which occurs automatically

        elif rnum == lenrooms+2:
            #back to hotel menu (end function)
            return

def employeemenu(newworkers):
    while 1:
        hprint('\nCurrent Employees:')
        
        emplen = len(h.employees)
        #Display emplyees
        for i in range(emplen):
            e = h.employees[i]
            print(' {}) {} {} - {}'.format(i+1,e.fname,e.lname,e.job))

        #Show other options
        hprint('\n {}) Find new employee'.format(emplen+1))
        hprint(' {}) Fire an employee'.format(emplen+2))
        hprint(' {}) Back to hotel menu'.format(emplen+3))
        hprint('Select an employee or other option:')

        #User input
        choice = getchoice(range(1,emplen+4))
        
        if choice in range(1,emplen+1):
            #display specific employee data
            e = h.employees[choice-1]
            hprint('{} {} - {}:\n  Gender: {}\n  Age: {}\n  Rate: ${}/hr\n  Ability level: {}/{}'
                   .format(e.fname,e.lname,e.job,e.gender,e.age,e.rate,e.ability,10))

            input('\nPress enter to return to employee menu.\n > ')
            
        elif choice == emplen + 1:
            #Menu to employ new worker from daily list of job-seekers (newworkers)
            hprint('\nFinding available workers...')
            
            if newworkers == []:
                hprint(' There are no workers available right now.')
            else:
                newnum = len(newworkers)
                #Show available workers
                for i in range(newnum):
                    ep = newworkers[i]
                    hprint(' {}) {} {} - ${}/hr'.format(i+1,ep.fname,ep.lname,ep.rate))

                #Show other options
                hprint('\n {}) Back to employee menu'.format(newnum+1))
                hprint('Select a worker to employ, or {} to go back.'.format(newnum+1))

                #User input
                choice = getchoice(range(1,newnum+2))
                
                if choice in range(1,newnum+1):
                    nw = newworkers[choice-1]
                    #Give new employee a job
                    hprint('Give {} {} a job:'.format(nw.fname,nw.lname))
                    #Available jobs are cleaner plus the respective job for each owned amenity
                    jobs = ['Cleaner']+[amenities[f][0] for f in h.amenities]
                    for j in range(len(jobs)):
                        hprint(' {}) {}'.format(j+1,jobs[j]))

                    #User input (again)
                    nw.job = jobs[getchoice(range(1,len(jobs)+1))-1]

                    #Move new worker to the employees list
                    h.employees.append(nw)
                    newworkers.remove(nw)

                    h.addxp(20)
                    hprint('Your new {}, {} {}, has been employed!'.format(nw.job,nw.fname,nw.lname))
                #No need for an else/elif, as the other option is 'back to employees', which occurs automatically
        elif choice == emplen + 2:
            #firing a worker
            hprint('\nSelect a worker to fire:')

            hprint(' Phil Hiett - NOBODY fires Phil Hiett')
            #display fireable workers
            for x in range(emplen-1):
                i = h.employees[x+1]
                hprint(' {}) {} {} - {} - ${}/hr - Ability level {}/10'
                       .format(x+1,i.fname,i.lname,i.job,i.rate,i.ability))

            hprint('\n {}) Back to employee menu'.format(emplen))

            fired = getchoice(range(1,emplen+1))
            
            if fired in range(1,emplen):
                w = h.employees[fired]
                hprint('\n{} {} has been fired'.format(w.fname,w.lname))
                h.employees.remove(w)
                del w
            #if they picked 'back', this stream of code ends here anyway
        else:
            #Back to hotel menu, updating the remaining available workers
            return newworkers

def amenitymenu():
    #Pretty much identical to the other menus
    while 1:
        hprint('\nCurrent amenities:')
        #display amenities
        if h.amenities == []:
            hprint(' Your hotel has no amenities.')
        else:
            for i in h.amenities:
                hprint(' '+i)

        #display options
        hprint('\n 1) Buy new amenity\n 2) Back to hotel menu')
        #user input
        choice = getchoice([1,2])
        if choice == 1:
            hprint('\n Available amenities:')
            #available amenities is [all amenities] minus [owned amenities]
            newamens = sorted(set(amenities.keys()).difference(h.amenities))
            if newamens == []:
                hprint('Your hotel has all possible amenities!')
            else:
                #display available amenities
                for i in range(len(newamens)):
                    hprint(' {}) {} - ${}'.format(i+1,newamens[i],amenities[newamens[i]][1]))
                hprint(' {}) Back to amenities'.format(len(newamens)+1))

                #get choice
                nm = getchoice(range(1,len(newamens)+2))
                if nm == len(newamens) + 1:
                    #back to amenity menu
                    pass
                else:
                    #user wants to buy a certain amenity
                    cost = amenities[newamens[nm-1]][1]
                    if h.bal >= cost:
                        h.bal -= cost
                        h.amenities.append(newamens[nm-1])
                        h.addxp(50)
                        hprint('Your hotel now has a {}!'.format(newamens[nm-1]))

                    else:
                        hprint("You don't have enough funds!")                       
        else:
            return

def advertisingmenu():
    while 1:
        #Display active advertisements
        hprint('\n Current advertisements:')
        if h.adverts == {}:
            hprint('  No advertisements are currently active')
        else:
            for i in list(h.adverts):
                hprint('  {} - {} days remaining'.format(i,h.adverts[i]))

        #Display available advertisements
        hprint('\n Available advertisements:')
        ads = sorted(set(advertisements).difference(set(h.adverts)))
        adlen = len(ads)
        
        if ads == []:
            hprint('  All advertisements are currently active.')
        else:
            for i in range(adlen):
                ad = ads[i]
                hprint('  {}) {} - ${} - Lasts {} days'.format(i+1,ad,advertisements[ad][2],advertisements[ad][0]))

        #User selection
        hprint('\n {}) Back to hotel menu\n Selection:'.format(adlen+1))
        choice = getchoice(range(1,adlen+2))
        if choice == adlen+1:
            #Back to hotel menu
            return
        else:
            newad = ads[choice-1]
            addata = advertisements[newad]
            #Try buying advertisment
            if h.bal >= addata[2]:
                #Sufficient funds; activate advertisement
                h.adverts[newad] = addata[0]
                h.bal -= addata[2]
                h.advert_level += addata[1]
                hprint('You are now advertising via {}'.format(newad))
            else:
                #Insufficient funds
                hprint("You don't have enough funds.")
                
def guestmenu():
    while 1:
        #display guests
        hprint('Current guests:')
        reslen = len(h.residents)
        for i in range(reslen):
            res = h.residents[i]
            hprint(' {}) {} {} - Room {}'.format(i+1,res.fname,res.lname,res.room.roomno))
        hprint('\n {}) Back to hotel menu'.format(reslen+1))
        #see my getchoice function (failsafe way of getting input)
        choice = getchoice(range(1,reslen+2))

        if choice in range(1,reslen+1):
            #display specific guest data
            e = h.residents[choice-1]
            hprint('{} {} - Room {}:\n  Gender: {}\n  Age: {}\n'
               .format(e.fname,e.lname,e.room.roomno,e.gender,e.age))
            input('Press enter to return to guest menu.\n > ')
        else:
            return
'''Run'''
#Welcome text
hprint('Welcome to Hotel Hype!')

#Create files if they don't exist
for i in ['hotels.txt','index.txt','rooms.txt','employees.txt','residents.txt']:
    open(i,'a').close()
    
#Run program
mainmenu()

