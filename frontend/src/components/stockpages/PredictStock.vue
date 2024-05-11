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
        return {
            stockData: [],
            stockCode: '',
        };
    },
    created() {
        this.stockCode = this.$route.params.stockcode;
        this.updateDimensions();
    },
    mounted() {
        window.addEventListener('resize', this.updateDimensions);
        this.fetchStockData();
    },
    beforeUnmount() {
        window.removeEventListener('resize', this.updateDimensions);
    },
    methods: {
        updateDimensions() {
            this.$nextTick(() => {
                const container = this.$refs.chart;
                if (!container) return;

                this.width = container.clientWidth;
                this.height = container.clientHeight;

                this.drawChart();
            });
        },
        fetchStockData() {
            axios.get(`/stock/${this.stockCode}/getpredict`, {})
                .then(response => {
                    const predictData = response.data.predict_data;
                    let currentDate = new Date();
                    currentDate.setDate(currentDate.getDate() + 1); // 從明天開始
                    for (let i = 0; i < Math.min(predictData.length, 5); i++) {
                        this.stockData.push({
                            date: currentDate.toISOString().slice(0, 10),
                            close: predictData[i],
                        });
                        currentDate.setDate(currentDate.getDate() + 1);
                    }
                    this.drawChart(); // 在數據加載完後呼叫
                })
                .catch(error => {
                    console.error('Error fetching stock data:', error);
                });
        },
        drawChart() {
            const container = this.$refs.chart;
            if (!container || !this.stockData.length) return;

            d3.select(container).select('svg').remove();

            const svg = d3.select(container)
                .append('svg')
                .attr('width', '100%')
                .attr('height', '100%')
                .style('background-color', 'white');

            const margin = { top: 20, right: 70, bottom: 60, left: 80 };
            const drawingWidth = this.width - margin.left - margin.right;
            const drawingHeight = this.height - margin.top - margin.bottom;

            const g = svg.append('g').attr('transform', `translate(${margin.left}, ${margin.top})`);

            const x = d3.scaleTime()
                .domain([d3.min(this.stockData, d => new Date(d.date)), d3.max(this.stockData, d => new Date(d.date))])
                .range([0, drawingWidth]);

            const yPrice = d3.scaleLinear()
                .domain([0, d3.max(this.stockData, d => d.close)])
                .range([drawingHeight, 0]);

            const line = d3.line()
                .x(d => x(new Date(d.date)))
                .y(d => yPrice(d.close));

            g.append('path')
                .datum(this.stockData)
                .attr('fill', 'none')
                .attr('stroke', '#be0027')
                .attr('stroke-width', 2)
                .attr('d', line);

            this.stockData.forEach(data => {
                g.append('circle')
                    .attr('cx', x(new Date(data.date)))
                    .attr('cy', yPrice(data.close))
                    .attr('r', 5)
                    .attr('fill', '#be0027');
            });

            g.append('g')
                .attr('transform', `translate(0, ${drawingHeight})`)
                .call(d3.axisBottom(x).ticks(d3.timeDay.every(1)).tickFormat(d3.timeFormat('%m/%d')));

            g.append('g').call(d3.axisLeft(yPrice));
        }
    }
}
</script>

<style scoped>
.predict-chart {
    width: 100%;
    height: 400px;
    margin-top: 15px;
    border: 2px solid #11862f;
}

</style>