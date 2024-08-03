import 'package:flutter/material.dart';
import 'package:data_table_2/data_table_2.dart';

class DataTable2TopAndTail extends DataTable2 {
  final int? alwaysOnScreenRow;

  DataTable2TopAndTail({
    super.key,
    required super.columns,
    super.sortColumnIndex,
    super.sortAscending = true,
    super.onSelectAll,
    super.decoration,
    super.dataRowColor,
    super.dataRowHeight,
    super.dataTextStyle,
    super.headingRowColor,
    super.fixedColumnsColor,
    super.fixedCornerColor,
    super.headingRowHeight,
    super.headingTextStyle,
    super.headingCheckboxTheme,
    super.datarowCheckboxTheme,
    super.horizontalMargin,
    super.checkboxHorizontalMargin,
    super.checkboxAlignment = Alignment.center,
    super.bottomMargin,
    super.columnSpacing,
    super.showHeadingCheckBox = true,
    super.showCheckboxColumn = true,
    super.showBottomBorder = false,
    super.dividerThickness,
    super.clipBehavior,
    super.minWidth,
    super.scrollController,
    super.horizontalScrollController,
    super.isVerticalScrollBarVisible,
    super.isHorizontalScrollBarVisible,
    super.empty,
    super.border,
    super.smRatio = 0.67,
    super.fixedTopRows = 1,
    super.fixedLeftColumns = 0,
    super.lmRatio = 1.2,
    super.sortArrowAnimationDuration = const Duration(milliseconds: 150),
    super.sortArrowIcon = Icons.arrow_upward,
    super.sortArrowBuilder,
    super.headingRowDecoration,
    required super.rows,
    this.alwaysOnScreenRow,
  }) : assert(alwaysOnScreenRow == null || alwaysOnScreenRow > 0,
            'alwaysOnScreenRow must be null or a positive integer');

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        return _DataTable2TopAndTailWidget(
          dataTable: this,
          constraints: constraints,
        );
      },
    );
  }
}

class _DataTable2TopAndTailWidget extends StatefulWidget {
  final DataTable2TopAndTail dataTable;
  final BoxConstraints constraints;

  const _DataTable2TopAndTailWidget({
    required this.dataTable,
    required this.constraints,
  });

  @override
  _DataTable2TopAndTailWidgetState createState() =>
      _DataTable2TopAndTailWidgetState();
}

class _DataTable2TopAndTailWidgetState
    extends State<_DataTable2TopAndTailWidget> {
  late ScrollController _verticalController;
  late List<DataRow> _rows;

  @override
  void initState() {
    super.initState();
    _verticalController = widget.dataTable.scrollController ??
        ScrollController();
    _rows = List.from(widget.dataTable.rows);
    _verticalController.addListener(_handleScroll);
  }

  @override
  void dispose() {
    _verticalController.removeListener(_handleScroll);
    if (widget.dataTable.scrollController == null) {
      _verticalController.dispose();
    }
    super.dispose();
  }

  void _handleScroll() {
    if (widget.dataTable.alwaysOnScreenRow != null) {
      setState(() {
        _updateRowsOrder();
      });
    }
  }

  void _updateRowsOrder() {
    final int alwaysOnScreenIndex = widget.dataTable.alwaysOnScreenRow! - 1;
    if (alwaysOnScreenIndex >= _rows.length) return;

    final double rowHeight = widget.dataTable.dataRowHeight ??
        Theme.of(context).dataTableTheme.dataRowMinHeight ??
        kMinInteractiveDimension;
    final double viewportHeight = widget.constraints.maxHeight;
    final double scrollOffset = _verticalController.offset;
    final int fixedTopRows = widget.dataTable.fixedTopRows;

    final double alwaysOnScreenRowPosition =
        (alwaysOnScreenIndex - fixedTopRows + 1) * rowHeight;
    final double bottomThreshold = scrollOffset + viewportHeight;
    final double topThreshold = scrollOffset + fixedTopRows * rowHeight;

    if (alwaysOnScreenRowPosition > bottomThreshold) {
      // Pin to bottom
      final DataRow movingRow = _rows.removeAt(alwaysOnScreenIndex);
      _rows.add(movingRow);
    } else if (alwaysOnScreenRowPosition < topThreshold &&
        alwaysOnScreenIndex >= fixedTopRows) {
      // Pin to top (just below fixed rows)
      final DataRow movingRow = _rows.removeAt(alwaysOnScreenIndex);
      _rows.insert(fixedTopRows, movingRow);
    } else if (alwaysOnScreenIndex < fixedTopRows ||
        (alwaysOnScreenRowPosition >= topThreshold &&
            alwaysOnScreenRowPosition <= bottomThreshold)) {
      // Restore original position
      _rows = List.from(widget.dataTable.rows);
    }
  }

  @override
  Widget build(BuildContext context) {
    return DataTable2(
      key: widget.dataTable.key,
      columns: widget.dataTable.columns,
      sortColumnIndex: widget.dataTable.sortColumnIndex,
      sortAscending: widget.dataTable.sortAscending,
      onSelectAll: widget.dataTable.onSelectAll,
      decoration: widget.dataTable.decoration,
      dataRowColor: widget.dataTable.dataRowColor,
      dataRowHeight: widget.dataTable.dataRowHeight,
      dataTextStyle: widget.dataTable.dataTextStyle,
      headingRowColor: widget.dataTable.headingRowColor,
      fixedColumnsColor: widget.dataTable.fixedColumnsColor,
      fixedCornerColor: widget.dataTable.fixedCornerColor,
      headingRowHeight: widget.dataTable.headingRowHeight,
      headingTextStyle: widget.dataTable.headingTextStyle,
      headingCheckboxTheme: widget.dataTable.headingCheckboxTheme,
      datarowCheckboxTheme: widget.dataTable.datarowCheckboxTheme,
      horizontalMargin: widget.dataTable.horizontalMargin,
      checkboxHorizontalMargin: widget.dataTable.checkboxHorizontalMargin,
      checkboxAlignment: widget.dataTable.checkboxAlignment,
      bottomMargin: widget.dataTable.bottomMargin,
      columnSpacing: widget.dataTable.columnSpacing,
      showHeadingCheckBox: widget.dataTable.showHeadingCheckBox,
      showCheckboxColumn: widget.dataTable.showCheckboxColumn,
      showBottomBorder: widget.dataTable.showBottomBorder,
      dividerThickness: widget.dataTable.dividerThickness,
      clipBehavior: widget.dataTable.clipBehavior,
      minWidth: widget.dataTable.minWidth,
      scrollController: _verticalController,
      horizontalScrollController: widget.dataTable.horizontalScrollController,
      isVerticalScrollBarVisible: widget.dataTable.isVerticalScrollBarVisible,
      isHorizontalScrollBarVisible:
          widget.dataTable.isHorizontalScrollBarVisible,
      empty: widget.dataTable.empty,
      border: widget.dataTable.border,
      smRatio: widget.dataTable.smRatio,
      fixedTopRows: widget.dataTable.fixedTopRows,
      fixedLeftColumns: widget.dataTable.fixedLeftColumns,
      lmRatio: widget.dataTable.lmRatio,
      sortArrowAnimationDuration: widget.dataTable.sortArrowAnimationDuration,
      sortArrowIcon: widget.dataTable.sortArrowIcon,
      sortArrowBuilder: widget.dataTable.sortArrowBuilder,
      headingRowDecoration: widget.dataTable.headingRowDecoration,
      rows: _rows,
    );
  }
}
