<template>
    <div>
        <div class="predict-chart" ref="chart"></div>
    </div>
</template>

<script>
import * as d3 from 'd3';
import axios from 'axios';

export default {
    name: 'PredictStock',
    data() {
        const today = new Date();
        const tenDaysAgo = new Date(today.setDate(today.getDate() - 10)).toISOString().slice(0, 10);
        const endDate = new Date().toISOString().slice(0, 10);

        return {
            startDate: tenDaysAgo,
            endDate: endDate,
            stockData: [],
            stockCode: '',  // 股票編號
        };
    },
    created() {
        // 重新從路由獲取股票編號
        this.stockCode = this.$route.params.stockcode;
    },
    mounted() {
        this.fetchStockData();
        this.drawChart();
    },
    methods: {
        fetchStockData() {
            axios.get(`/stock/${this.stockCode}/getpredict`, {
            })
                .then(response => {
                    const predictData = response.data.predict_data;

                    // 將預測數據添加到stockData中
                    for (let i = 0; i < predictData.length; i++) {
                        const futureDate = new Date();
                        futureDate.setDate(futureDate.getDate() + i + 1);
                        this.stockData.push({
                            date: futureDate.toISOString().slice(0, 10),
                            close: predictData[i],
                        });
                    }

                    this.$nextTick(() => {
                        setTimeout(() => {
                            this.updateChart(this.$refs.chart);
                        }, 500);  // 延遲1秒後再更新圖表
                    });
                    console.log(predictData);
                })
                .catch(error => {
                    console.error('Error fetching stock data:', error);
                });
        },
        drawChart() {
            const container = this.$refs.chart;
            const resizeObserver = new ResizeObserver(() => {
                this.updateChart(container);
            });
            resizeObserver.observe(container);
        },

        updateChart(container) {
            if (!container || this.stockData.length === 0) return;
            d3.select(container).select('svg').remove();

            const width = container.clientWidth || 600; // 為避免寬度為0，提供默認最小寬度
            const height = container.clientHeight;

            const svg = d3.select(container)
                .append('svg')
                .attr('width', '100%') // 使用百分比以適應容器
                .attr('height', '100%') // 使用百分比以適應容器
                .style('background-color', 'white');

            const margin = { top: 20, right: 70, bottom: 60, left: 40 };
            const drawingWidth = width - margin.left - margin.right;
            const drawingHeight = height - margin.top - margin.bottom;

            const g = svg.append('g').attr('transform', `translate(${margin.left}, ${margin.top})`);

            const parseDate = d3.timeParse('%Y-%m-%d');

            this.stockData.forEach(d => {
                d.date = parseDate(d.date);
                d.close = +d.close;
            });

            const x = d3.scaleTime()
                .domain([d3.min(this.stockData, d => d.date), d3.max(this.stockData, d => d.date)])
                .range([0, drawingWidth]);

            const yPrice = d3.scaleLinear()
                .domain([0, d3.max(this.stockData, d => d.close)])
                .range([drawingHeight, 0]);

            const line = d3.line()
                .x(d => x(d.date))
                .y(d => yPrice(d.close));

            g.append('path')
                .datum(this.stockData)
                .attr('fill', 'none')
                .attr('stroke', '#be0027')
                .attr('stroke-width', 2)
                .attr('d', line);

            const totalDays = d3.timeDay.count(d3.min(this.stockData, d => d.date), d3.max(this.stockData, d => d.date)) + 1;
            const tickInterval = totalDays > 30 ? 7 : 1; // 如果總天數超過30天，則每七天顯示一次日期，否則每天都顯示

            let lastYear = null;
            let lastMonth = null;
            g.append('g')
                .attr('transform', `translate(0, ${drawingHeight})`)
                .call(d3.axisBottom(x).ticks(d3.timeDay.every(tickInterval)).tickFormat(date => {
                    const year = date.getFullYear();
                    const month = date.getMonth();
                    if (lastYear !== year) {
                        lastYear = year;
                        lastMonth = month;
                        return d3.timeFormat('%Y')(date);
                    } else if (lastMonth !== month) {
                        lastMonth = month;
                        return d3.timeFormat('%m-%d')(date);
                    } else if (this.stockData.length <= 30) { // 如果資料點少於或等於30，則顯示日
                        return d3.timeFormat('%m-%d')(date);
                    } else {
                        return '';
                    }
                }));

            g.append('g')
                .call(d3.axisLeft(yPrice));
        }
    }
}
</script>

<style scoped>
.history-chart {
    width: 100%;
    height: 400px;
    margin-top: 15px;
    border: 2px solid #11862f;
}
</style>