# 基于多分类模型的鸢尾花识别与可视化演示系统

本项目严格按照实训题目要求实现：使用 `sklearn` 内置鸢尾花数据集，训练 KNN 和决策树两种多分类模型，提供预测菜单，并将 CSV 数据集与可视化结果保存到本地。

## 功能

- 加载 `sklearn.datasets.load_iris()` 内置数据集。
- 导出数据集为 `Iris.csv`。
- 查看数据统计信息、类别分布。
- 划分训练集和测试集。
- 训练 KNN、决策树模型。
- 输出准确率与分类报告。
- 输入萼片、花瓣尺寸预测花卉类别。
- 保存四特征两两对比散点分类图。
- 保存决策树可视化图。
- 保存模型准确率对比柱状图。
- 保存混淆矩阵热力图。
- 提供简易交互菜单与异常捕获。

## 环境要求

- Python
- pandas
- scikit-learn
- matplotlib
- graphviz

主程序启动时会先检测本机是否存在 Graphviz 的 `dot` 命令；如果没有检测到，会自动调用 `scripts/install_graphviz.ps1` 安装 Graphviz，并添加到用户环境变量 `PATH`。

如需单独安装 Graphviz，也可以运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_graphviz.ps1 -PathScope User
```

验证：

```powershell
where.exe dot
dot -V
```

## 安装依赖

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 运行

```powershell
python main.py
```

## 输出文件

运行程序后会生成：

- `Iris.csv`
- `outputs/data_statistics.csv`
- `outputs/classification_metrics.txt`
- `outputs/pairwise_scatter.png`
- `outputs/decision_tree.png`
- `outputs/model_accuracy.png`
- `outputs/knn_confusion_matrix.png`
- `outputs/decision_tree_confusion_matrix.png`

`iris.data` 是项目中的原始参考数据文件，正式程序按题目约束使用 `sklearn` 内置数据集。

