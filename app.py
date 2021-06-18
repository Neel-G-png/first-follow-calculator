import sys
from flask import Flask , jsonify,redirect, request,render_template
from flask.helpers import url_for

app = Flask(__name__)
app.config["DEBUG"] = True

# non_terminals = ['A','B','C','D','E','F']
# FIRST = {'A':{'!','a','ds','%'},'B':{'!','a','ds','%'},'C':{'!','a','ds','%'},'D':{'!','a','ds','%'},'E':{'!','a','ds','%'},'F':{'!','a','ds','%'},}
# FOLLOW = {'A':{'v','k','*','#'},'B':{'v','k','*','#'},'C':{'v','k','*','#'},'D':{'v','k','*','#'},'E':{'v','k','*','#'},'F':{'v','k','*','#'},}

no_of_terminals = 0
terminals = []
no_of_non_terminals = 0
non_terminals = []
starting_symbol = "_"
no_of_productions = 0
productions = []
productions_dict = {}

FIRST = {}
FOLLOW = {}
j=0
alter_dict_check = {}

def first(string):
    alternatives = []
    
    first_ = set()
    if string in non_terminals:
        alternatives = productions_dict[string]

        for alternative in alternatives:
            if alter_dict_check[alternative]!=-1:
                first_2 = first(alternative)
                first_ = first_ |first_2

    elif string in terminals:
        first_ = {string}

    elif string=='' or string=='@':
        first_ = {'@'}

    else:
        first_2 = first(string[0])
        if '@' in first_2:
            i = 1
            while '@' in first_2:
                #print("inside while")

                first_ = first_ | (first_2 - {'@'})
                #print('string[i:]=', string[i:])
                if string[i:] in terminals:
                    first_ = first_ | {string[i:]}
                    break
                elif string[i:] == '':
                    first_ = first_ | {'@'}
                    break
                first_2 = first(string[i:])
                first_ = first_ | first_2 - {'@'}
                i += 1
        else:
            first_ = first_ | first_2


    #print("returning for first({})".format(string),first_)
    return  first_


def follow(nT):
    #print("inside follow({})".format(nT))
    follow_ = set()
    #print("FOLLOW", FOLLOW)
    prods = productions_dict.items()
    if nT==starting_symbol:
        follow_ = follow_ | {'$'}
    for nt,rhs in prods:
        #print("nt to rhs", nt,rhs)
        for alt in rhs:
            for char in alt:
                if char==nT:
                    following_str = alt[alt.index(char) + 1:]
                    if following_str=='':
                        if nt==nT:
                            continue
                        else:
                            follow_ = follow_ | follow(nt)
                    else:
                        follow_2 = first(following_str)
                        if '@' in follow_2:
                            follow_ = follow_ | follow_2-{'@'}
                            follow_ = follow_ | follow(nt)
                        else:
                            follow_ = follow_ | follow_2
    #print("returning for follow({})".format(nT),follow_)
    return follow_

@app.route("/",methods = ['POST','GET'])
def input_data():
    global no_of_terminals,terminals,no_of_non_terminals,non_terminals,starting_symbol,no_of_productions,productions,productions_dict,j,alter_dict_check
    global FIRST,FOLLOW
    data = {
        "starting_symbol":starting_symbol,
        "non_terminals":non_terminals,
        "FIRST":FIRST,
        "FOLLOW":FOLLOW
    }

    if request.method == 'POST':
        no_of_terminals = request.form['not']
        terminals = request.form['ts']
        no_of_non_terminals = request.form['nont']
        non_terminals = request.form['nts']
        starting_symbol = request.form['ss']
        no_of_productions = request.form['nop']
        productions = request.form['ps']
        context = {
            "no_of_terminals":no_of_terminals,
            "terminals":terminals,
            "no_of_non_terminals":no_of_non_terminals,
            "non_terminals":non_terminals,
            "starting_symbol":starting_symbol,
            "no_of_productions":no_of_productions,
            "productions":productions,
        }
        terminals = terminals.split(",")
        non_terminals = non_terminals.split(",")
        productions = productions.split(",")
        # print(type(terminals))


        # productions_dict = {}

        for nT in non_terminals:
            productions_dict[nT] = []


        # print("\nproductions_dict",productions_dict)

        for production in productions:
            nonterm_to_prod = production.split("->")
            # print("\nNON TERM ",nonterm_to_prod)
            alternatives = nonterm_to_prod[1].split("/")
            for alternative in alternatives:
                productions_dict[nonterm_to_prod[0]].append(alternative)

        #print("productions_dict",productions_dict)
        for nt in non_terminals:
            for i in range(len(productions_dict[nt])):
                if nt == productions_dict[nt][i][0]:
                    alter_dict_check[productions_dict[nt][i]]=-1
                    # print(f"\nNT : {nt},   string : {productions_dict[nt]}")
                else:
                    alter_dict_check[productions_dict[nt][i]]=1
            
        # print("nonterm_to_prod",nonterm_to_prod)
        print("\n \t alternatives dict : ",alter_dict_check)
        # return "done"

       

        for non_terminal in non_terminals:
            FIRST[non_terminal] = set()

        for non_terminal in non_terminals:
            FOLLOW[non_terminal] = set()

        #print("FIRST",FIRST)

        for non_terminal in non_terminals:
            j=0
            FIRST[non_terminal] = FIRST[non_terminal] | first(non_terminal)

        print("FIRST :",FIRST)
        # exit()

        FOLLOW[starting_symbol] = FOLLOW[starting_symbol] | {'$'}
        # print(FOLLOW[starting_symbol])
        for non_terminal in non_terminals:
            FOLLOW[non_terminal] = FOLLOW[non_terminal] | follow(non_terminal)


        for non_terminal in non_terminals:
          FIRST[non_terminal] = list(FIRST[non_terminal])
          FOLLOW[non_terminal] = list(FOLLOW[non_terminal])

        data = {
        "starting_symbol":starting_symbol,
        "non_terminals":non_terminals,
        "productions":productions_dict,
        "FIRST":FIRST,
        "FOLLOW":FOLLOW
        }
        print("\nPRODUCTIONS_DICT : ", productions_dict)
        # pass
        return render_template("app.html", data=data)
    else:
        data["starting_symbol"] = "_"
        no_of_terminals = 0
        terminals = []
        no_of_non_terminals = 0
        non_terminals = []
        starting_symbol = "_"
        no_of_productions = 0
        productions = []
        productions_dict = {}
    return render_template("app.html", data=data)

if __name__ == "__main__":
    app.run(threaded=True)