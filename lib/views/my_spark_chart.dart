import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:syncfusion_flutter_charts/charts.dart';

class ChartData {
  ChartData(this.x, this.y);

  final int x;
  final double y;
}

class MySparkChart extends StatelessWidget {
  MySparkChart({
    super.key,
    required this.data,
    required this.labelTextCallback,
  }) {
    chartData = [];
    for (int i = 0; i < data.length; i++) {
      chartData.add(ChartData(i, data[i]));
    }
  }

  final List<double> data;
  late List<ChartData> chartData;
  final Text Function(double) labelTextCallback;

  @override
  Widget build(BuildContext context) {
    return SfCartesianChart(
      borderWidth: 0,
      plotAreaBorderWidth: 0,
      primaryXAxis: NumericAxis(isVisible: false),
      primaryYAxis: NumericAxis(isVisible: false),
      series: <CartesianSeries>[
        LineSeries<ChartData, int>(
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
        ),
      ],
    );
  }
}
