# Risk Parity

Risk parity is a type of asset allocation strategy that has become increasingly popular in the aftermath of the global financial crisis.、

Risk parity is an advanced portfolio technique often used by hedge funds. It typically requires quantitative methodology which makes its allocations more advanced than simplified allocation strategies. Simplified allocation strategies such as 60/40 are based on MPT and hold a percentage of asset classes, such as 60% stocks and 40% bonds, for standard diversification and exposure within one's investment portfolio. This allocation seeks to generally target a hypothetical risk level graphed at the intersection of the efficient frontier and capital market line. In simplified allocation strategies using just stocks and bonds, allocations are usually more heavily weighted towards equities for investors willing to take on more risk. Risk averse investors will typically have a higher weight in bonds for capital preservation.



## formula

there are N assets（$ a_1, a_2,...,a_n$）, 

$yield =(r_1,r_2,...,r_n)$,

$asset\_weight = (w_1,w_2,...,w_n)$,



$portfolio\_return = \sum_i^N(w_i * r_i)$ 



$portfolio\_risk= \sqrt{X^T\sum X} = \sqrt{\sum^N_i(x_i^2*\sigma^2_i) + \sum_i\sum_{j\neq i}{x_j*\sigma_{i,j}}}$



* **Marginal Risk Contribution(MRC)**



即资产$i$ 的边际风险贡献定义为组合总风险对资产$i$ 权重的偏导数，由偏导数的物理意义，可知该风险贡献刻画的是单个资产配置权重的微小变化对组合总体波动率带来的影响。基于这个边际风险贡献，引出第二个定义
$$
MRC_i = \part_{x_i}\sigma(x) = \frac{\part\sigma(x)}{\part x_i} = \frac{\sum_j{x_j * \sigma_{i,j}}}{\part(x)} = \frac{x_i^2\sigma_i^2 + \sum_{i\neq j}{x_j * \sigma_{i,j}}}{\part(x)}
$$


* **Total Risk Contribution(TRC)**

即资产*i* 对总风险的贡献为该资产权重与其边际风险贡献的[乘积](https://www.zhihu.com/search?q=乘积&search_source=Entity&hybrid_search_source=Entity&hybrid_search_extra={"sourceType"%3A"article"%2C"sourceId"%3A36650070})
$$
TRC_i = \sigma_i(x) = x_i * MRC_i = \frac{\sum_j{x_ix_j * \sigma_{i,j}}}{\sigma(x)}
$$



$$
\sigma(x) = \sum^n_{i=1}TRC_i = \sum^n_{i=1}{x_i\frac{\part(x)}{\part x_i}}
$$




这个公式证明可以自己推导一下。推导的过程中可以反向思维一下，就是知道了总风险的定义，要如何设计各个资产的风险，才能把整体的风险完全的拆到每个资产上。这个证明过程不难，但是我认为对理解平价风险中风险的拆分特别重要，基本上风险能拆到独立的单个资产上了，后续的工作就非常简单了。

简单的对各个资产的风险做一个归一化处理如下:


$$
\frac{TRC_i}{\sigma(x)} = \frac{x_i\frac{\part(x)}{\part x_i}}{\sigma(x)} =\frac{x_i(\sum x)_i}{X^T\sum X}
$$
其中![[公式]](https://www.zhihu.com/equation?tex=%EF%BC%88%5CSigma+X%29_%7Bi%7D+) 为向量 ![[公式]](https://www.zhihu.com/equation?tex=%5CSigma+X)的第*i*个元素， 由此引出风险平价模型的基本定义：将组合的总风险平均的分摊到每个资产上，即





定义三：风险平价


$$
TRC_i = TRC_j \quad \forall i,j \\
x_i(\sum x)_i = x_j(\sum x)_j \quad \forall i,j
$$


最后 ![[公式]](https://www.zhihu.com/equation?tex=x_%7Bi%7D) 求解有两种方式，一种是解析解，另一种是非线性规划求数值解。个人比较推荐非线性数值规划求数值解，即解一个如下的优化问题：


$$
x^* = argmin(\sum^n_{i}\sum^n_{j}(TRC_i-TRC_j)^2) \\
=argmin(\sum^n_{i}\sum^n_{j}(x_i(\sum x)_i-x_j(\sum x)_j)^2) \\

st \quad \sum^n_{i} x_i =1 \\
0 \leq X \leq 1
$$

# ref
1. [资产配置模型学习笔记（二）： 风险平价模型](https://zhuanlan.zhihu.com/p/36650070)
2. [资产配置的魔法棒之五：使用风险平价模型进行资产配置](https://zhuanlan.zhihu.com/p/349132505)
3. [【资产配置】一文读懂风险预算模型](https://zhuanlan.zhihu.com/p/401323179)
4. [风险平价Risk Parity模型 最简明清晰解读（附Excel模板下载）](https://www.sohu.com/a/279062829_750247)
5. [你真的搞懂了风险平价吗？](https://zhuanlan.zhihu.com/p/38301218)


