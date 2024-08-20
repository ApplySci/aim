import 'package:flutter/material.dart';
import 'package:syncfusion_flutter_charts/charts.dart';

class ChartData {
  ChartData(this.x, this.y);
  final int x;
  final double y;
}

enum MySparkChartType { bar, line }

class MySparkChart extends StatelessWidget {
  const MySparkChart({
    super.key,
    this.axisLineColor,
    this.chartType = MySparkChartType.line,
    required this.data,
    required this.labelTextCallback,
  });

  final MySparkChartType chartType;
  final List<num> data;
  final Widget Function(double) labelTextCallback;
  final Color? axisLineColor;

  @override
  Widget build(BuildContext context) {
    CartesianSeries series;
    List<ChartData> chartData = [];
    for (int i = 0; i < data.length; i++) {
      chartData.add(ChartData(i, 1.0 * data[i]));
    }
    switch (chartType) {
      case MySparkChartType.line:
        series = LineSeries<ChartData, int>(
          dataSource: chartData,
          xValueMapper: (ChartData data, _) => data.x,
          yValueMapper: (ChartData data, _) => data.y,
          markerSettings: const MarkerSettings(isVisible: true),
          dataLabelSettings: DataLabelSettings(
            isVisible: true,
            builder: (dynamic data, dynamic point, dynamic series,
                int pointIndex, int seriesIndex) {
              return labelTextCallback(point.y);
            },
          ),
        );
        break;
      case MySparkChartType.bar:
        series = BarSeries<ChartData, int>(
          dataSource: chartData,
          xValueMapper: (ChartData data, _) => data.x,
          yValueMapper: (ChartData data, _) => data.y,
          pointColorMapper: (ChartData data, _) => data.y < 0
              ? Colors.red
              : Colors.blue,
          markerSettings: const MarkerSettings(isVisible: true),
          dataLabelSettings: DataLabelSettings(
            isVisible: true,
            labelAlignment: ChartDataLabelAlignment.outer,
            builder: (dynamic data, dynamic point, dynamic series,
                int pointIndex, int seriesIndex) {
              return labelTextCallback(point.y);
            },
          ),
        );
        break;
    }
    return SfCartesianChart(
      borderWidth: 0,
      plotAreaBorderWidth: 0,
      primaryXAxis: axisLineColor == null
          ? CategoryAxis(isVisible: false)
          : CategoryAxis(
              isVisible: true,
              axisLine: AxisLine(
                color: axisLineColor,
              ),
              crossesAt: 0,
        majorTickLines: const MajorTickLines(width: 0),
        minorTickLines: const MinorTickLines(width: 0),
        majorGridLines: const MajorGridLines(width: 0),
        minorGridLines: const MinorGridLines(width: 0),
        labelStyle: const TextStyle(fontSize: 0),
            ),
      primaryYAxis: NumericAxis(isVisible: false),
      series: <CartesianSeries>[series],
    );
  }
}
