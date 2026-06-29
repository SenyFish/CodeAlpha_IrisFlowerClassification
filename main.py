from pathlib import Path

import graphviz
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier, export_graphviz


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
CSV_PATH = BASE_DIR / "Iris.csv"

FEATURE_NAMES = [
    "sepal_length",
    "sepal_width",
    "petal_length",
    "petal_width",
]


def ensure_output_dir():
    OUTPUT_DIR.mkdir(exist_ok=True)


def load_and_export_data():
    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=FEATURE_NAMES)
    df["species"] = [iris.target_names[target] for target in iris.target]
    df.to_csv(CSV_PATH, index=False, encoding="utf-8")
    return iris, df


def print_data_statistics(df):
    ensure_output_dir()
    print("\n[数据统计]")
    print(f"样本数量: {len(df)}")
    print(f"特征数量: {len(FEATURE_NAMES)}")
    print(f"类别数量: {df['species'].nunique()}")
    print("\n统计信息:")
    print(df.describe())
    print("\n类别分布:")
    print(df["species"].value_counts())
    print(f"\nCSV 已导出: {CSV_PATH}")
    statistics_path = OUTPUT_DIR / "data_statistics.csv"
    df.describe().to_csv(statistics_path, encoding="utf-8")
    print(f"数据统计已保存: {statistics_path}")


def split_data(iris):
    return train_test_split(
        iris.data,
        iris.target,
        test_size=0.2,
        random_state=42,
        stratify=iris.target,
    )


def train_models(x_train, y_train):
    models = {
        "KNN": KNeighborsClassifier(n_neighbors=5),
        "Decision Tree": DecisionTreeClassifier(random_state=42),
    }
    for model in models.values():
        model.fit(x_train, y_train)
    return models


def evaluate_models(models, x_test, y_test, target_names, verbose=True):
    ensure_output_dir()
    results = {}
    report_lines = ["[模型评估]"]
    if verbose:
        print("\n[模型评估]")
    for name, model in models.items():
        y_pred = model.predict(x_test)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, target_names=target_names)
        results[name] = {
            "model": model,
            "accuracy": accuracy,
            "y_pred": y_pred,
        }
        report_lines.append(f"\n{name} 准确率: {accuracy:.4f}")
        report_lines.append(f"{name} 分类报告:")
        report_lines.append(report)
        if verbose:
            print(f"\n{name} 准确率: {accuracy:.4f}")
            print(f"{name} 分类报告:")
            print(report)
    report_path = OUTPUT_DIR / "classification_metrics.txt"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    if verbose:
        print(f"分类指标已保存: {report_path}")
    return results


def save_pairwise_scatter(df):
    color_map = {
        "setosa": "#2b8cbe",
        "versicolor": "#e34a33",
        "virginica": "#31a354",
    }
    figure, axes = plt.subplots(4, 4, figsize=(12, 12))
    for row, y_feature in enumerate(FEATURE_NAMES):
        for col, x_feature in enumerate(FEATURE_NAMES):
            ax = axes[row][col]
            if row == col:
                for species, color in color_map.items():
                    values = df[df["species"] == species][x_feature]
                    ax.hist(values, alpha=0.65, color=color, label=species)
            else:
                for species, color in color_map.items():
                    subset = df[df["species"] == species]
                    ax.scatter(
                        subset[x_feature],
                        subset[y_feature],
                        s=20,
                        alpha=0.8,
                        color=color,
                        label=species,
                    )
            if row == 3:
                ax.set_xlabel(x_feature)
            if col == 0:
                ax.set_ylabel(y_feature)
    handles, labels = axes[0][0].get_legend_handles_labels()
    figure.legend(handles, labels, loc="upper right")
    figure.suptitle("Iris Four-Feature Pairwise Classification Scatter", fontsize=14)
    figure.tight_layout(rect=(0, 0, 0.95, 0.96))
    output_path = OUTPUT_DIR / "pairwise_scatter.png"
    figure.savefig(output_path, dpi=200)
    plt.close(figure)
    print(f"四特征两两对比散点分类图已保存: {output_path}")


def save_decision_tree_graph(model, iris):
    dot_data = export_graphviz(
        model,
        out_file=None,
        feature_names=FEATURE_NAMES,
        class_names=iris.target_names,
        filled=True,
        rounded=True,
        special_characters=True,
    )
    graph = graphviz.Source(dot_data)
    output_stem = OUTPUT_DIR / "decision_tree"
    graph.render(str(output_stem), format="png", cleanup=True)
    print(f"决策树可视化图已保存: {output_stem}.png")


def save_accuracy_bar(results):
    names = list(results.keys())
    accuracies = [results[name]["accuracy"] for name in names]
    figure, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(names, accuracies, color=["#2b8cbe", "#31a354"])
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Accuracy")
    ax.set_title("Model Accuracy Comparison")
    for bar, accuracy in zip(bars, accuracies):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.02,
            f"{accuracy:.4f}",
            ha="center",
        )
    output_path = OUTPUT_DIR / "model_accuracy.png"
    figure.tight_layout()
    figure.savefig(output_path, dpi=200)
    plt.close(figure)
    print(f"模型准确率对比柱状图已保存: {output_path}")


def save_confusion_matrix(results, y_test, target_names):
    for name, result in results.items():
        figure, ax = plt.subplots(figsize=(6, 5))
        ConfusionMatrixDisplay.from_predictions(
            y_test,
            result["y_pred"],
            display_labels=target_names,
            cmap="Blues",
            ax=ax,
        )
        ax.set_title(f"{name} Confusion Matrix")
        output_path = OUTPUT_DIR / f"{name.lower().replace(' ', '_')}_confusion_matrix.png"
        figure.tight_layout()
        figure.savefig(output_path, dpi=200)
        plt.close(figure)
        print(f"{name} 混淆矩阵热力图已保存: {output_path}")


def save_visualizations(iris, df, results, y_test):
    ensure_output_dir()
    save_pairwise_scatter(df)
    save_decision_tree_graph(results["Decision Tree"]["model"], iris)
    save_accuracy_bar(results)
    save_confusion_matrix(results, y_test, iris.target_names)


def predict_flower(models, target_names):
    try:
        print("\n请输入 4 个尺寸数值，单位为 cm。")
        sepal_length = float(input("萼片长度 sepal length: "))
        sepal_width = float(input("萼片宽度 sepal width: "))
        petal_length = float(input("花瓣长度 petal length: "))
        petal_width = float(input("花瓣宽度 petal width: "))
        sample = [[sepal_length, sepal_width, petal_length, petal_width]]
        print("\n[预测结果]")
        for name, model in models.items():
            prediction = model.predict(sample)[0]
            print(f"{name}: {target_names[prediction]}")
    except ValueError:
        print("输入错误：请输入有效数字。")
    except Exception as exc:
        print(f"预测失败: {exc}")


def prepare_system():
    iris, df = load_and_export_data()
    x_train, x_test, y_train, y_test = split_data(iris)
    models = train_models(x_train, y_train)
    results = evaluate_models(models, x_test, y_test, iris.target_names, verbose=False)
    return iris, df, models, results, x_test, y_test


def show_menu():
    print("\n====== 鸢尾花识别与可视化演示系统 ======")
    print("1. 查看数据统计并导出 CSV")
    print("2. 训练并评估 KNN、决策树模型")
    print("3. 输入尺寸预测花卉种类")
    print("4. 保存全部可视化图表")
    print("0. 退出")


def main():
    try:
        iris, df, models, results, x_test, y_test = prepare_system()
        while True:
            show_menu()
            choice = input("请选择功能: ").strip()
            if choice == "1":
                print_data_statistics(df)
            elif choice == "2":
                evaluate_models(models, x_test, y_test, iris.target_names)
            elif choice == "3":
                predict_flower(models, iris.target_names)
            elif choice == "4":
                save_visualizations(iris, df, results, y_test)
            elif choice == "0":
                print("已退出系统。")
                break
            else:
                print("无效选择，请输入 0-4。")
    except KeyboardInterrupt:
        print("\n用户中断，程序已退出。")
    except Exception as exc:
        print(f"系统运行失败: {exc}")


if __name__ == "__main__":
    main()
