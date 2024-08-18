import 'package:flutter/material.dart';
import '/views/data_table_2d.dart';

enum RowLocation { top, middle, bottom }

class DataTable2FixedLine extends StatefulWidget {
  final double? minWidth;
  final int? fixedRow;
  final List<DataColumn> columns;
  final List<DataRow> rows;
  final double? columnSpacing;

  const DataTable2FixedLine({
    super.key,
    this.minWidth,
    this.fixedRow,
    required this.columns,
    required this.rows,
    this.columnSpacing,
  })
      : assert(fixedRow == null || fixedRow >= 0),
        assert(fixedRow == null || fixedRow < rows.length);

  @override
  State<DataTable2FixedLine> createState() => _DataTable2FixedLineState();
}

class _DataTable2FixedLineState extends State<DataTable2FixedLine> {
  final ScrollController _verticalController = ScrollController();
  RowLocation rowLocation = RowLocation.middle;
  late double rowHeight;
  late double viewportHeight;
  final int fixedTopRows = 1;
  final GlobalKey rowKey = GlobalKey();
  final GlobalKey tableKey = GlobalKey();

  @override
  void initState() {
    print('initialising DataTable2_fixed_line');
    super.initState();
    _verticalController.addListener(_handleScroll);

    WidgetsBinding.instance.addPostFrameCallback((_) {

      final RenderBox rowRenderBox =
          rowKey.currentContext?.findRenderObject() as RenderBox;

      rowHeight = rowRenderBox.size.height;

      final RenderBox tableRenderBox =
          rowKey.currentContext?.findRenderObject() as RenderBox;

      viewportHeight = tableRenderBox.size.height;
    });

  }

  @override
  void dispose() {
    _verticalController.removeListener(_handleScroll);
    _verticalController.dispose();
    super.dispose();
  }

  void _handleScroll() {
    if (widget.fixedRow == null) return;
    RowLocation newLocation = _calculateFixedRowLocation();
    if (newLocation != rowLocation) {
      setState(() => rowLocation = newLocation);
    }
  }

  RowLocation _calculateFixedRowLocation() {
    final int idx = widget.fixedRow! - 1;
    final double scroll = _verticalController.offset;
    final double idxPos = rowHeight * (idx - fixedTopRows + 1);

    if (idxPos < scroll + fixedTopRows * rowHeight) return RowLocation.top;
    if (idxPos > scroll + viewportHeight) return RowLocation.bottom;
    return RowLocation.middle;
  }

  @override
  Widget build(context) {
    int fixedTopRows = 1;
    int fixedBottomRows = 0;
    List<DataRow> rows;

    if (widget.fixedRow == null || rowLocation == RowLocation.middle) {
      rows = widget.rows;
    } else {
      rows = List.from(widget.rows);
      DataRow fixedDataRow = rows.removeAt(widget.fixedRow!);
      if (rowLocation == RowLocation.top) {
        fixedTopRows = 2;
        rows.insert(0, fixedDataRow);
      } else { // RowLocation.bottom:
        fixedBottomRows = 1;
        rows.add(fixedDataRow);
      }
    }

    return DataTable2d(
      scrollController: _verticalController,
      columns: widget.columns,
      rows: rows,
      columnSpacing: widget.columnSpacing,
      minWidth: widget.minWidth,
      fixedBottomRows: fixedBottomRows,
      fixedTopRows: fixedTopRows,
    );
  }
}
