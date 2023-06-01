import csv
from decisiontree import DecisionTree
from argparse import ArgumentParser
from sys import argv, exit


def main():
    parser = ArgumentParser(description='ID3 Decision Tree')

    parser.add_argument('-e', '--examples', type=str,
                        help='csv file with the examples used to build the tree.')
    parser.add_argument('-t', '--tests', type=str,
                        help='CSV file with the tests to be made.')

    args = parser.parse_args()

    if len(argv) == 1:
        parser.print_help()
        exit(0)

    with open(args.examples, 'rt') as fd:
        exemplosBuf = csv.reader(fd)
        firstRow = exemplosBuf.__next__()

        exemplos = []
        for i in exemplosBuf:
            exemplos.append(i)
            
        atributos = {}

        for i in range(len(firstRow)):
            atributos[firstRow[i]] = i

        classe = firstRow[-1]
        fd.close()

    arvore = DecisionTree(exemplos, atributos, classe)
    print(arvore)

    if args.tests is not None:
        with open(args.tests, 'rt') as fd:
            exemplosBuf = csv.reader(fd)
            firstRow = exemplosBuf.__next__()

            for aux in exemplosBuf:
                if not aux:
                    break

                dicio = {}
                for i in range(len(firstRow)):
                    dicio[firstRow[i]] = aux[i]

                resul = arvore.classify(dicio)
                if resul is None:
                    print(arvore.mostCommon())
                else:
                    print(resul)


if __name__ == '__main__':
    main()
