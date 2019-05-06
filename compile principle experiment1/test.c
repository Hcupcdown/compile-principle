#include <iostream>
#include <fstream>
#include <string>
#include <vector>
using namespace std;

//词
typedef struct Node
{
	string value;
	int code;
	string cate;
}Node;

//已经定义了的标识符和整数
typedef struct exis
{
	string value;
	int code;
}exis;

const vector<string> key = { "if","else","for","while","switch","case","int","char","bool","include","define","return","using","namespace","const","struct","typedef" };//关键字
const vector<string> ope = { "+","-","*","/","!","%",">=",">","<=","<","==","=","!=","#" };//运算符
const vector<string> sep = { ",",";","{","}",")","(","\"","'" };//分隔符
vector <exis> exis_iden;//已经存在的标识符
vector <exis> exis_num;//已经存在的数字

//对比是否为关键字
int compare_key(string in)
{
	for (int i = 0; i < key.size(); i++)
	{
		if (in._Equal(key[i]))
		{
			return 1000 + i;
		}
	}
	return -1;
}

//对比是否为运算符
int compare_ope(string in)
{
	for (int i = 0; i < ope.size(); i++)
	{
		if (in._Equal(ope[i]))
		{
			return 2000 + i;
		}
	}
	return -1;
}

//对比是否为分隔符
int compare_sep(string in)
{
	for (int i = 0; i < sep.size(); i++)
	{
		if (in._Equal(sep[i]))
		{
			return 3000 + i;
		}
	}
	return -1;
}

//判断是否为已经存在的标识符或数字
int compare_exis(string in)
{
	for (int i = 0; i < exis_iden.size(); i++)
	{
		if (in._Equal(exis_iden[i].value))
		{
			return exis_iden[i].code;
		}
	}
	for (int i = 0; i < exis_num.size(); i++)
	{
		if (in._Equal(exis_num[i].value))
		{
			return exis_num[i].code;
		}
	}
	return -1;
}

//清空当前保存节点
void clear_node(Node* nownode)
{
	nownode->value = "";
	nownode->code = 0;
	nownode->cate = "";
}

int main()
{
	ifstream infile("test.c");
	char c;

	//记录已经存在的标识符和整数个数
	int ide_flag = 0;
	int num_flag = 0;

	//存放词
	vector<Node> node;
	Node nownode;
	exis nowiden;

	infile >> noskipws;
	infile >> c;

	//读入字符主循环
	while (!infile.eof())
	{
		//处理注释
		if (c == '/')
		{
			infile >> c;
			if (c == '/')
			{
				while (c != 13 && c != 10)
				{
					infile >> c;
				}
			}
			else
			{
				if (c == '*')
				{
					infile >> c;
					while (c != '*')
					{
						infile >> c;
					}
					infile.seekg(2, ios::cur);
					infile >> c;
				}
				else
				{
					infile.seekg(-2, ios::cur);
					infile >> c;
				}
			}
		}

		//识别字符串
		if (c == '_' || (c <= 'Z' && c >= 'A') || (c >= 'a' && c <= 'z'))
		{
			nownode.value.append(1, c);
			while (!infile.eof())
			{
				infile >> c;
				if (c == '_' || (c <= 'Z' && c >= 'A') || (c >= 'a' && c <= 'z') || (c >= '0' && c<= '9'))
					nownode.value.append(1, c);
				else
				{
					infile.seekg(-1, ios::cur);
					break;
				}
					
			}

			//如果这个是关键字
			nownode.code = compare_key(nownode.value);
			nownode.cate = "keywords";
			if (nownode.code == -1)
			{
				nownode.code = compare_exis(nownode.value);
				nownode.cate = "identifier";
				//如果这个标识符还不存在
				if (nownode.code == -1)
				{
					nownode.code = 4000 + ide_flag;
					ide_flag++;
					nowiden.code = nownode.code;
					nowiden.value = nownode.value;
					exis_iden.push_back(nowiden);
				}
			}
			node.push_back(nownode);
			clear_node(&nownode);
			infile >> c;
			continue;
		}

		//识别数字
		if (c >= '0' && c <= '9')
		{
			nownode.value.append(1, c);
			while (!infile.eof())
			{
				infile >> c;
				if (c >= '0' && c <= '9')
					nownode.value.append(1, c);
				else
				{
					infile.seekg(-1, ios::cur);
					break;
				}
			}
			nownode.code = compare_exis(nownode.value);
			if (nownode.code == -1)
			{
				nownode.code = 5000 + num_flag;
				num_flag++;
			}
			nownode.cate = "integer";
			node.push_back(nownode);
			clear_node(&nownode);
			infile >> c;
			continue;
		}

		//处理大于等于，小于等于
		if (c == '>' || c == '<')
		{
			nownode.value.append(1, c);
			if (!infile.eof())
			{
				infile >> c;
				if (c == '=')
				{
					nownode.value.append(1, c);
				}
				else 
				{
					infile.seekg(-1, ios::cur);
				}
			}
			nownode.code = compare_ope(nownode.value);
			nownode.cate = "operator";
			node.push_back(nownode);
			clear_node(&nownode);
			infile >> c;
			continue;
		}

		if (c == '=' || c == '!')
		{
			nownode.value.append(1, c);
			if (!infile.eof())
			{
				infile >> c;
				if (c == '=')
				{
					nownode.value.append(1, c);
				}
				else
				{
					infile.seekg(-1, ios::cur);
				}
			}
			nownode.code = compare_ope(nownode.value);
			nownode.cate = "operator";
			node.push_back(nownode);
			clear_node(&nownode);
			infile >> c;
			continue;
		}

		//处理其他字符
		if (c != 10 && c != 13 && c != ' '&&c!='	')
		{

			nownode.value.append(1, c);
			nownode.code = compare_ope(nownode.value);
			nownode.cate = "operator";
			if (nownode.code == -1)
			{
				nownode.code = compare_sep(nownode.value);
				nownode.cate = "separator";
			}
			node.push_back(nownode);
			clear_node(&nownode);
			infile >> c;
			continue;
		}
		infile >> c;
	}

	//输出分析结果
	for (int i = 0; i < node.size(); i++)
	{
		cout <<"(" <<node[i].code << " \""<<node[i].value <<"\" " << node[i].cate <<")"<< endl;
	}
	infile.close();
	system("pause");
	return 0;
}