from math import log2
from sys import maxsize
from copy import deepcopy

class DecisionTree:
    minimoElem = 4

    def __init__(self, examples, atributos, classe):
        self.classe = classe
        self.transforms = {}
        self.objetivosPossiveis = []
        self.root = None

        for exampple in examples:
            target = exampple[-1]
            if target not in self.objetivosPossiveis:
                self.objetivosPossiveis.append(target)

        self.atributosG_Str_Int = atributos
        self.atributosG_Int_Str = {v: k for k, v in atributos.items()}

        for i in range(1, len(atributos)):
            try:
                float(examples[0][i])
                self.transform(examples, i)
            except ValueError:
                pass

        self.examples = deepcopy(examples)
        self.made_tree(examples, deepcopy(atributos))
        self.root.rearrange()

    def classify(self, dict):
        for key, val in self.transforms.items():
            try:
                dict[key] = val[val.index(float(dict[key]))]
            except ValueError:
                return None
        return self.root.classify(dict)

    def entropy(self, examples, atributo, flag=False):
        difer_atribute = []
        diferAtrExamp = []

        for i in range(len(examples)):
            try:
                aux = difer_atribute.index(examples[i][atributo])
                diferAtrExamp[aux].append(i)
            except ValueError:
                difer_atribute.append(examples[i][atributo])
                diferAtrExamp.append([i])

        if flag:
            for i in range(len(self.examples)):
                try:
                    difer_atribute.index(self.examples[i][atributo])
                except ValueError:
                    difer_atribute.append(self.examples[i][atributo])
                    diferAtrExamp.append([])

            classeRep = [[0] * len(self.objetivosPossiveis)
                         for _ in range(len(difer_atribute))]

            for i in range(len(diferAtrExamp)):
                for ex in diferAtrExamp[i]:
                    classeRep[i][self.objetivosPossiveis.index(
                        examples[ex][-1])] += 1

            return difer_atribute, diferAtrExamp, classeRep

        del difer_atribute
        res = 0

        for conjunto in diferAtrExamp:
            classeRep = [0] * len(self.objetivosPossiveis)
            for i in conjunto:
                classeRep[self.objetivosPossiveis.index(examples[i][-1])] += 1
            aux = 0
            for i in classeRep:
                aux += -(i / len(conjunto)) * log2(i / len(conjunto) + 1e-20)

            res += (len(conjunto) / len(examples)) * aux
        return res

    def made_tree(self, examples, attributes):
        decision = self.make_decision(examples, attributes)
        self.root = self.ID3(examples, decision, attributes)

    def make_decision(self, exemplos, atributes):
        _entropy = [None] * (len(self.atributosG_Str_Int) - 1)
        for key, val in atributes.items():
            if key != self.classe and key != 'ID':
                _entropy[val] = self.entropy(exemplos, val)
        _entropy[0] = maxsize
        _entropy = [x if x is not None else maxsize for x in _entropy]
        decision = _entropy.index(min(_entropy))
        return self.atributosG_Int_Str[decision]

    def ID3(self, examples, target_attribute, attributes):
        del attributes[target_attribute]

        attribute_names, attribute_examples, final_answers = self.entropy(
            examples, self.atributosG_Str_Int[target_attribute], True)

        node = NodeRoot(target_attribute)
        incomplete = []

        for i in range(len(attribute_names)):
            flag = True
            if not attribute_examples[i]:
                incomplete.append(i)
                continue
            for x in final_answers[i]:
                if x != 0:
                    if flag:
                        class_label = self.objetivosPossiveis[final_answers[i].index(
                            x)]
                        flag = False
                    else:
                        incomplete.append(i)
                        flag = True
                        break

            if not flag:
                node.append(
                    Leaf(attribute_names[i], class_label, len(attribute_examples[i])))

        if len(attributes) > 2:
            for i in incomplete:
                aux_examples = [examples[x] for x in attribute_examples[i]]
                if aux_examples:
                    decision = self.make_decision(aux_examples, attributes)
                    sub_tree = self.ID3(
                        aux_examples, decision, deepcopy(attributes))
                    node.append(
                        Jump(attribute_names[i], sub_tree, len(attribute_examples[i])))
                else:
                    node.append(Leaf(attribute_names[i], self.mostCommon(), 0))
        else:
            for i in incomplete:
                answer = attribute_names[i]
                count = len(attribute_examples[i])
                label = self.objetivosPossiveis[final_answers[i].index(
                    max(final_answers[i]))]
                node.append(Leaf(answer, label, count))

        return node

    def mostCommon(self):
        classeRep = [0] * len(self.objetivosPossiveis)

        for aux in self.examples:
            classeRep[self.objetivosPossiveis.index(aux[-1])] += 1

        return self.objetivosPossiveis[classeRep.index(max(classeRep))]

    def transform(self, exemplos, index):
        lista = [(float(exemplos[u][index]), exemplos[u][-1])
                 for u in range(len(exemplos))]
        lista.sort()
        aux = []

        the_flag = False
        i = 0

        for num, target in lista:
            if i == 0:
                test = target
                first = num
            elif i >= self.minimoElem:
                if test != target or the_flag:
                    aux.append(Interval(first, num))
                    first = num
                    test = target
                    the_flag = False
                    i = 0

            elif test != target:
                the_flag = True
            i += 1

        aux.append(Interval(first, num + 0.1))

        for u in range(len(exemplos)):
            exemplos[u][index] = aux[aux.index(float(exemplos[u][index]))]

        self.transforms[self.atributosG_Int_Str[index]] = aux

    def __str__(self):
        return self.root.my_str()


class Branch:
    pass


class Leaf(Branch):
    def __init__(self, answer, label, counter):
        self.answer = answer
        self.label = label
        self.counter = counter

    def __str__(self):
        return f"{self.answer}: {self.label} ({self.counter})\n"

    def my_str(self, depth):
        return '\t' * depth + f"{self.answer}: {self.label} ({self.counter})\n"

    def classify(self, data_dict):
        return self.label

    def rearrange(self):
        pass


class Jump(Branch):
    def __init__(self, answer, jump, counter):
        self.answer = answer
        self.jump = jump
        self.counter = counter

    def __str__(self):
        return str(self.answer) + ':\n' + str(self.jump)

    def my_str(self, depth):
        return '\t' * depth + str(self.answer) + ':\n' + self.jump.my_str(depth + 1)

    def classify(self, dictionary):
        return self.jump.classify(dictionary)

    def rearrange(self):
        self.jump.rearrange()


class NodeRoot:

    def __init__(self, attribute):
        self.attribute = attribute
        self.answers = []

    def append(self, item):
        self.answers.append(item)

    def __str__(self):
        res = '<' + self.attribute + '>\n'
        for answer in self.answers:
            res += str(answer)

        return res

    def my_str(self, depth=0):
        res = '\t' * depth + '<' + self.attribute + '>\n'
        for answer in self.answers:
            res += answer.my_str(depth + 1)

        return res

    def classify(self, dictionary):
        user_answer = dictionary[self.attribute]
        for answer in self.answers:
            if isinstance(answer.answer, Interval):
                if answer.answer.is_inside(user_answer):
                    return answer.classify(dictionary)
                continue

            if answer.answer == user_answer:
                return answer.classify(dictionary)

    def rearrange(self):
        if isinstance(self.answers[0].answer, Interval):
            answer_aux = []

            ve = [(self.answers[i].answer,
                   (lambda x: self.answers[i].label if isinstance(self.answers[i], Leaf) else None)(i), i) for i in
                  range(len(self.answers))]
            ve.sort()

            i = -1
            last = None 
            for _, classe, index in ve:
                if classe is None or last != classe:
                    answer_aux.append([index])
                    last = classe
                    i += 1
                    continue
                answer_aux[i].append(index)

            del ve

            answer_tmp = []

            for list in answer_aux:
                if isinstance(self.answers[list[0]], Jump):
                    answer_tmp.append(self.answers[list[0]])
                    continue

                minimum = self.answers[list[0]].answer.minimum
                maximum = self.answers[list[0]].answer.maximum
                label = self.answers[list[0]].label
                count = 0

                for i in list:
                    count += self.answers[i].counter
                    maximum = max(maximum, self.answers[i].answer.maximum)

                answer_tmp.append(
                    Leaf(Interval(minimum, maximum), label, count))

            self.answers = answer_tmp

        for answer in self.answers:
            answer.rearrange()


class Interval:
    def __init__(self, minimum, maximum):
        self.minimum = minimum
        self.maximum = maximum

    def is_inside(self, other):
        if not isinstance(other, Interval):
            return False

        if self.minimum <= other.minimum and other.maximum <= self.maximum:
            return True
        else:
            return False

    def __eq__(self, other):
        if isinstance(self, type(other)):
            if self.minimum == other.minimum and self.maximum == other.maximum:
                return True
            else:
                return False

        if self.minimum <= other < self.maximum:
            return True
        else:
            return False

    def __lt__(self, other):
        if isinstance(self, type(other)):
            return self.maximum <= other.minimum

    def __str__(self):
        return str(self.minimum) + ' <= x < ' + str(self.maximum)
