# adapted from Alice Miller's social golfer page at http://breakoutroom.pythonanywhere.com/allocate/
seats = [
	[
		[128, 32, 64, 96],
		[1, 33, 65, 97],
		[2, 34, 66, 98],
		[3, 35, 67, 99],
		[4, 36, 68, 100],
		[5, 37, 69, 101],
		[6, 38, 70, 102],
		[7, 39, 71, 103],
		[8, 40, 72, 104],
		[9, 41, 73, 105],
		[10, 42, 74, 106],
		[11, 43, 75, 107],
		[12, 44, 76, 108],
		[13, 45, 77, 109],
		[14, 46, 78, 110],
		[15, 47, 79, 111],
		[16, 48, 80, 112],
		[17, 49, 81, 113],
		[18, 50, 82, 114],
		[19, 51, 83, 115],
		[20, 52, 84, 116],
		[21, 53, 85, 117],
		[22, 54, 86, 118],
		[23, 55, 87, 119],
		[24, 56, 88, 120],
		[25, 57, 89, 121],
		[26, 58, 90, 122],
		[27, 59, 91, 123],
		[28, 60, 92, 124],
		[29, 61, 93, 125],
		[30, 62, 94, 126],
		[31, 63, 95, 127]
	],

	[
		[128, 33, 66, 99],
		[1, 32, 67, 98],
		[2, 35, 64, 97],
		[3, 34, 65, 96],
		[4, 37, 70, 103],
		[5, 36, 71, 102],
		[6, 39, 68, 101],
		[7, 38, 69, 100],
		[8, 41, 74, 107],
		[9, 40, 75, 106],
		[10, 43, 72, 105],
		[11, 42, 73, 104],
		[12, 45, 78, 111],
		[13, 44, 79, 110],
		[14, 47, 76, 109],
		[15, 46, 77, 108],
		[16, 49, 82, 115],
		[17, 48, 83, 114],
		[18, 51, 80, 113],
		[19, 50, 81, 112],
		[20, 53, 86, 119],
		[21, 52, 87, 118],
		[22, 55, 84, 117],
		[23, 54, 85, 116],
		[24, 57, 90, 123],
		[25, 56, 91, 122],
		[26, 59, 88, 121],
		[27, 58, 89, 120],
		[28, 61, 94, 127],
		[29, 60, 95, 126],
		[30, 63, 92, 125],
		[31, 62, 93, 124]
	],

	[
		[128, 34, 68, 102],
		[1, 35, 69, 103],
		[2, 32, 70, 100],
		[3, 33, 71, 101],
		[4, 38, 64, 98],
		[5, 39, 65, 99],
		[6, 36, 66, 96],
		[7, 37, 67, 97],
		[8, 42, 76, 110],
		[9, 43, 77, 111],
		[10, 40, 78, 108],
		[11, 41, 79, 109],
		[12, 46, 72, 106],
		[13, 47, 73, 107],
		[14, 44, 74, 104],
		[15, 45, 75, 105],
		[16, 50, 84, 118],
		[17, 51, 85, 119],
		[18, 48, 86, 116],
		[19, 49, 87, 117],
		[20, 54, 80, 114],
		[21, 55, 81, 115],
		[22, 52, 82, 112],
		[23, 53, 83, 113],
		[24, 58, 92, 126],
		[25, 59, 93, 127],
		[26, 56, 94, 124],
		[27, 57, 95, 125],
		[28, 62, 88, 122],
		[29, 63, 89, 123],
		[30, 60, 90, 120],
		[31, 61, 91, 121]
	],

	[
		[128, 35, 70, 101],
		[1, 34, 71, 100],
		[2, 33, 68, 103],
		[3, 32, 69, 102],
		[4, 39, 66, 97],
		[5, 38, 67, 96],
		[6, 37, 64, 99],
		[7, 36, 65, 98],
		[8, 43, 78, 109],
		[9, 42, 79, 108],
		[10, 41, 76, 111],
		[11, 40, 77, 110],
		[12, 47, 74, 105],
		[13, 46, 75, 104],
		[14, 45, 72, 107],
		[15, 44, 73, 106],
		[16, 51, 86, 117],
		[17, 50, 87, 116],
		[18, 49, 84, 119],
		[19, 48, 85, 118],
		[20, 55, 82, 113],
		[21, 54, 83, 112],
		[22, 53, 80, 115],
		[23, 52, 81, 114],
		[24, 59, 94, 125],
		[25, 58, 95, 124],
		[26, 57, 92, 127],
		[27, 56, 93, 126],
		[28, 63, 90, 121],
		[29, 62, 91, 120],
		[30, 61, 88, 123],
		[31, 60, 89, 122]
	],

	[
		[128, 36, 69, 97],
		[1, 37, 68, 96],
		[2, 38, 71, 99],
		[3, 39, 70, 98],
		[4, 32, 65, 101],
		[5, 33, 64, 100],
		[6, 34, 67, 103],
		[7, 35, 66, 102],
		[8, 44, 77, 105],
		[9, 45, 76, 104],
		[10, 46, 79, 107],
		[11, 47, 78, 106],
		[12, 40, 73, 109],
		[13, 41, 72, 108],
		[14, 42, 75, 111],
		[15, 43, 74, 110],
		[16, 52, 85, 113],
		[17, 53, 84, 112],
		[18, 54, 87, 115],
		[19, 55, 86, 114],
		[20, 48, 81, 117],
		[21, 49, 80, 116],
		[22, 50, 83, 119],
		[23, 51, 82, 118],
		[24, 60, 93, 121],
		[25, 61, 92, 120],
		[26, 62, 95, 123],
		[27, 63, 94, 122],
		[28, 56, 89, 125],
		[29, 57, 88, 124],
		[30, 58, 91, 127],
		[31, 59, 90, 126]
	],

	[
		[128, 37, 71, 98],
		[1, 36, 70, 99],
		[2, 39, 69, 96],
		[3, 38, 68, 97],
		[4, 33, 67, 102],
		[5, 32, 66, 103],
		[6, 35, 65, 100],
		[7, 34, 64, 101],
		[8, 45, 79, 106],
		[9, 44, 78, 107],
		[10, 47, 77, 104],
		[11, 46, 76, 105],
		[12, 41, 75, 110],
		[13, 40, 74, 111],
		[14, 43, 73, 108],
		[15, 42, 72, 109],
		[16, 53, 87, 114],
		[17, 52, 86, 115],
		[18, 55, 85, 112],
		[19, 54, 84, 113],
		[20, 49, 83, 118],
		[21, 48, 82, 119],
		[22, 51, 81, 116],
		[23, 50, 80, 117],
		[24, 61, 95, 122],
		[25, 60, 94, 123],
		[26, 63, 93, 120],
		[27, 62, 92, 121],
		[28, 57, 91, 126],
		[29, 56, 90, 127],
		[30, 59, 89, 124],
		[31, 58, 88, 125]
	],

	[
		[128, 38, 65, 103],
		[1, 39, 64, 102],
		[2, 36, 67, 101],
		[3, 37, 66, 100],
		[4, 34, 69, 99],
		[5, 35, 68, 98],
		[6, 32, 71, 97],
		[7, 33, 70, 96],
		[8, 46, 73, 111],
		[9, 47, 72, 110],
		[10, 44, 75, 109],
		[11, 45, 74, 108],
		[12, 42, 77, 107],
		[13, 43, 76, 106],
		[14, 40, 79, 105],
		[15, 41, 78, 104],
		[16, 54, 81, 119],
		[17, 55, 80, 118],
		[18, 52, 83, 117],
		[19, 53, 82, 116],
		[20, 50, 85, 115],
		[21, 51, 84, 114],
		[22, 48, 87, 113],
		[23, 49, 86, 112],
		[24, 62, 89, 127],
		[25, 63, 88, 126],
		[26, 60, 91, 125],
		[27, 61, 90, 124],
		[28, 58, 93, 123],
		[29, 59, 92, 122],
		[30, 56, 95, 121],
		[31, 57, 94, 120]
	],

	[
		[128, 39, 67, 100],
		[1, 38, 66, 101],
		[2, 37, 65, 102],
		[3, 36, 64, 103],
		[4, 35, 71, 96],
		[5, 34, 70, 97],
		[6, 33, 69, 98],
		[7, 32, 68, 99],
		[8, 47, 75, 108],
		[9, 46, 74, 109],
		[10, 45, 73, 110],
		[11, 44, 72, 111],
		[12, 43, 79, 104],
		[13, 42, 78, 105],
		[14, 41, 77, 106],
		[15, 40, 76, 107],
		[16, 55, 83, 116],
		[17, 54, 82, 117],
		[18, 53, 81, 118],
		[19, 52, 80, 119],
		[20, 51, 87, 112],
		[21, 50, 86, 113],
		[22, 49, 85, 114],
		[23, 48, 84, 115],
		[24, 63, 91, 124],
		[25, 62, 90, 125],
		[26, 61, 89, 126],
		[27, 60, 88, 127],
		[28, 59, 95, 120],
		[29, 58, 94, 121],
		[30, 57, 93, 122],
		[31, 56, 92, 123]
	],

	[
		[128, 56, 80, 104],
		[1, 57, 81, 105],
		[2, 58, 82, 106],
		[3, 59, 83, 107],
		[4, 60, 84, 108],
		[5, 61, 85, 109],
		[6, 62, 86, 110],
		[7, 63, 87, 111],
		[8, 48, 88, 96],
		[9, 49, 89, 97],
		[10, 50, 90, 98],
		[11, 51, 91, 99],
		[12, 52, 92, 100],
		[13, 53, 93, 101],
		[14, 54, 94, 102],
		[15, 55, 95, 103],
		[16, 40, 64, 120],
		[17, 41, 65, 121],
		[18, 42, 66, 122],
		[19, 43, 67, 123],
		[20, 44, 68, 124],
		[21, 45, 69, 125],
		[22, 46, 70, 126],
		[23, 47, 71, 127],
		[24, 32, 72, 112],
		[25, 33, 73, 113],
		[26, 34, 74, 114],
		[27, 35, 75, 115],
		[28, 36, 76, 116],
		[29, 37, 77, 117],
		[30, 38, 78, 118],
		[31, 39, 79, 119]
	],

	[
		[128, 57, 82, 107],
		[1, 56, 83, 106],
		[2, 59, 80, 105],
		[3, 58, 81, 104],
		[4, 61, 86, 111],
		[5, 60, 87, 110],
		[6, 63, 84, 109],
		[7, 62, 85, 108],
		[8, 49, 90, 99],
		[9, 48, 91, 98],
		[10, 51, 88, 97],
		[11, 50, 89, 96],
		[12, 53, 94, 103],
		[13, 52, 95, 102],
		[14, 55, 92, 101],
		[15, 54, 93, 100],
		[16, 41, 66, 123],
		[17, 40, 67, 122],
		[18, 43, 64, 121],
		[19, 42, 65, 120],
		[20, 45, 70, 127],
		[21, 44, 71, 126],
		[22, 47, 68, 125],
		[23, 46, 69, 124],
		[24, 33, 74, 115],
		[25, 32, 75, 114],
		[26, 35, 72, 113],
		[27, 34, 73, 112],
		[28, 37, 78, 119],
		[29, 36, 79, 118],
		[30, 39, 76, 117],
		[31, 38, 77, 116]
	],

	[
		[128, 58, 84, 110],
		[1, 59, 85, 111],
		[2, 56, 86, 108],
		[3, 57, 87, 109],
		[4, 62, 80, 106],
		[5, 63, 81, 107],
		[6, 60, 82, 104],
		[7, 61, 83, 105],
		[8, 50, 92, 102],
		[9, 51, 93, 103],
		[10, 48, 94, 100],
		[11, 49, 95, 101],
		[12, 54, 88, 98],
		[13, 55, 89, 99],
		[14, 52, 90, 96],
		[15, 53, 91, 97],
		[16, 42, 68, 126],
		[17, 43, 69, 127],
		[18, 40, 70, 124],
		[19, 41, 71, 125],
		[20, 46, 64, 122],
		[21, 47, 65, 123],
		[22, 44, 66, 120],
		[23, 45, 67, 121],
		[24, 34, 76, 118],
		[25, 35, 77, 119],
		[26, 32, 78, 116],
		[27, 33, 79, 117],
		[28, 38, 72, 114],
		[29, 39, 73, 115],
		[30, 36, 74, 112],
		[31, 37, 75, 113]
	],

	[
		[128, 59, 86, 109],
		[1, 58, 87, 108],
		[2, 57, 84, 111],
		[3, 56, 85, 110],
		[4, 63, 82, 105],
		[5, 62, 83, 104],
		[6, 61, 80, 107],
		[7, 60, 81, 106],
		[8, 51, 94, 101],
		[9, 50, 95, 100],
		[10, 49, 92, 103],
		[11, 48, 93, 102],
		[12, 55, 90, 97],
		[13, 54, 91, 96],
		[14, 53, 88, 99],
		[15, 52, 89, 98],
		[16, 43, 70, 125],
		[17, 42, 71, 124],
		[18, 41, 68, 127],
		[19, 40, 69, 126],
		[20, 47, 66, 121],
		[21, 46, 67, 120],
		[22, 45, 64, 123],
		[23, 44, 65, 122],
		[24, 35, 78, 117],
		[25, 34, 79, 116],
		[26, 33, 76, 119],
		[27, 32, 77, 118],
		[28, 39, 74, 113],
		[29, 38, 75, 112],
		[30, 37, 72, 115],
		[31, 36, 73, 114]
	],

	[
		[128, 60, 85, 105],
		[1, 61, 84, 104],
		[2, 62, 87, 107],
		[3, 63, 86, 106],
		[4, 56, 81, 109],
		[5, 57, 80, 108],
		[6, 58, 83, 111],
		[7, 59, 82, 110],
		[8, 52, 93, 97],
		[9, 53, 92, 96],
		[10, 54, 95, 99],
		[11, 55, 94, 98],
		[12, 48, 89, 101],
		[13, 49, 88, 100],
		[14, 50, 91, 103],
		[15, 51, 90, 102],
		[16, 44, 69, 121],
		[17, 45, 68, 120],
		[18, 46, 71, 123],
		[19, 47, 70, 122],
		[20, 40, 65, 125],
		[21, 41, 64, 124],
		[22, 42, 67, 127],
		[23, 43, 66, 126],
		[24, 36, 77, 113],
		[25, 37, 76, 112],
		[26, 38, 79, 115],
		[27, 39, 78, 114],
		[28, 32, 73, 117],
		[29, 33, 72, 116],
		[30, 34, 75, 119],
		[31, 35, 74, 118]
	],

	[
		[128, 61, 87, 106],
		[1, 60, 86, 107],
		[2, 63, 85, 104],
		[3, 62, 84, 105],
		[4, 57, 83, 110],
		[5, 56, 82, 111],
		[6, 59, 81, 108],
		[7, 58, 80, 109],
		[8, 53, 95, 98],
		[9, 52, 94, 99],
		[10, 55, 93, 96],
		[11, 54, 92, 97],
		[12, 49, 91, 102],
		[13, 48, 90, 103],
		[14, 51, 89, 100],
		[15, 50, 88, 101],
		[16, 45, 71, 122],
		[17, 44, 70, 123],
		[18, 47, 69, 120],
		[19, 46, 68, 121],
		[20, 41, 67, 126],
		[21, 40, 66, 127],
		[22, 43, 65, 124],
		[23, 42, 64, 125],
		[24, 37, 79, 114],
		[25, 36, 78, 115],
		[26, 39, 77, 112],
		[27, 38, 76, 113],
		[28, 33, 75, 118],
		[29, 32, 74, 119],
		[30, 35, 73, 116],
		[31, 34, 72, 117]
	],

	[
		[128, 62, 81, 111],
		[1, 63, 80, 110],
		[2, 60, 83, 109],
		[3, 61, 82, 108],
		[4, 58, 85, 107],
		[5, 59, 84, 106],
		[6, 56, 87, 105],
		[7, 57, 86, 104],
		[8, 54, 89, 103],
		[9, 55, 88, 102],
		[10, 52, 91, 101],
		[11, 53, 90, 100],
		[12, 50, 93, 99],
		[13, 51, 92, 98],
		[14, 48, 95, 97],
		[15, 49, 94, 96],
		[16, 46, 65, 127],
		[17, 47, 64, 126],
		[18, 44, 67, 125],
		[19, 45, 66, 124],
		[20, 42, 69, 123],
		[21, 43, 68, 122],
		[22, 40, 71, 121],
		[23, 41, 70, 120],
		[24, 38, 73, 119],
		[25, 39, 72, 118],
		[26, 36, 75, 117],
		[27, 37, 74, 116],
		[28, 34, 77, 115],
		[29, 35, 76, 114],
		[30, 32, 79, 113],
		[31, 33, 78, 112]
	],

	[
		[128, 63, 83, 108],
		[1, 62, 82, 109],
		[2, 61, 81, 110],
		[3, 60, 80, 111],
		[4, 59, 87, 104],
		[5, 58, 86, 105],
		[6, 57, 85, 106],
		[7, 56, 84, 107],
		[8, 55, 91, 100],
		[9, 54, 90, 101],
		[10, 53, 89, 102],
		[11, 52, 88, 103],
		[12, 51, 95, 96],
		[13, 50, 94, 97],
		[14, 49, 93, 98],
		[15, 48, 92, 99],
		[16, 47, 67, 124],
		[17, 46, 66, 125],
		[18, 45, 65, 126],
		[19, 44, 64, 127],
		[20, 43, 71, 120],
		[21, 42, 70, 121],
		[22, 41, 69, 122],
		[23, 40, 68, 123],
		[24, 39, 75, 116],
		[25, 38, 74, 117],
		[26, 37, 73, 118],
		[27, 36, 72, 119],
		[28, 35, 79, 112],
		[29, 34, 78, 113],
		[30, 33, 77, 114],
		[31, 32, 76, 115]
	],

	[
		[128, 40, 88, 112],
		[1, 41, 89, 113],
		[2, 42, 90, 114],
		[3, 43, 91, 115],
		[4, 44, 92, 116],
		[5, 45, 93, 117],
		[6, 46, 94, 118],
		[7, 47, 95, 119],
		[8, 32, 80, 120],
		[9, 33, 81, 121],
		[10, 34, 82, 122],
		[11, 35, 83, 123],
		[12, 36, 84, 124],
		[13, 37, 85, 125],
		[14, 38, 86, 126],
		[15, 39, 87, 127],
		[16, 56, 72, 96],
		[17, 57, 73, 97],
		[18, 58, 74, 98],
		[19, 59, 75, 99],
		[20, 60, 76, 100],
		[21, 61, 77, 101],
		[22, 62, 78, 102],
		[23, 63, 79, 103],
		[24, 48, 64, 104],
		[25, 49, 65, 105],
		[26, 50, 66, 106],
		[27, 51, 67, 107],
		[28, 52, 68, 108],
		[29, 53, 69, 109],
		[30, 54, 70, 110],
		[31, 55, 71, 111]
	],

	[
		[128, 41, 90, 115],
		[1, 40, 91, 114],
		[2, 43, 88, 113],
		[3, 42, 89, 112],
		[4, 45, 94, 119],
		[5, 44, 95, 118],
		[6, 47, 92, 117],
		[7, 46, 93, 116],
		[8, 33, 82, 123],
		[9, 32, 83, 122],
		[10, 35, 80, 121],
		[11, 34, 81, 120],
		[12, 37, 86, 127],
		[13, 36, 87, 126],
		[14, 39, 84, 125],
		[15, 38, 85, 124],
		[16, 57, 74, 99],
		[17, 56, 75, 98],
		[18, 59, 72, 97],
		[19, 58, 73, 96],
		[20, 61, 78, 103],
		[21, 60, 79, 102],
		[22, 63, 76, 101],
		[23, 62, 77, 100],
		[24, 49, 66, 107],
		[25, 48, 67, 106],
		[26, 51, 64, 105],
		[27, 50, 65, 104],
		[28, 53, 70, 111],
		[29, 52, 71, 110],
		[30, 55, 68, 109],
		[31, 54, 69, 108]
	],

	[
		[128, 42, 92, 118],
		[1, 43, 93, 119],
		[2, 40, 94, 116],
		[3, 41, 95, 117],
		[4, 46, 88, 114],
		[5, 47, 89, 115],
		[6, 44, 90, 112],
		[7, 45, 91, 113],
		[8, 34, 84, 126],
		[9, 35, 85, 127],
		[10, 32, 86, 124],
		[11, 33, 87, 125],
		[12, 38, 80, 122],
		[13, 39, 81, 123],
		[14, 36, 82, 120],
		[15, 37, 83, 121],
		[16, 58, 76, 102],
		[17, 59, 77, 103],
		[18, 56, 78, 100],
		[19, 57, 79, 101],
		[20, 62, 72, 98],
		[21, 63, 73, 99],
		[22, 60, 74, 96],
		[23, 61, 75, 97],
		[24, 50, 68, 110],
		[25, 51, 69, 111],
		[26, 48, 70, 108],
		[27, 49, 71, 109],
		[28, 54, 64, 106],
		[29, 55, 65, 107],
		[30, 52, 66, 104],
		[31, 53, 67, 105]
	],

	[
		[128, 43, 94, 117],
		[1, 42, 95, 116],
		[2, 41, 92, 119],
		[3, 40, 93, 118],
		[4, 47, 90, 113],
		[5, 46, 91, 112],
		[6, 45, 88, 115],
		[7, 44, 89, 114],
		[8, 35, 86, 125],
		[9, 34, 87, 124],
		[10, 33, 84, 127],
		[11, 32, 85, 126],
		[12, 39, 82, 121],
		[13, 38, 83, 120],
		[14, 37, 80, 123],
		[15, 36, 81, 122],
		[16, 59, 78, 101],
		[17, 58, 79, 100],
		[18, 57, 76, 103],
		[19, 56, 77, 102],
		[20, 63, 74, 97],
		[21, 62, 75, 96],
		[22, 61, 72, 99],
		[23, 60, 73, 98],
		[24, 51, 70, 109],
		[25, 50, 71, 108],
		[26, 49, 68, 111],
		[27, 48, 69, 110],
		[28, 55, 66, 105],
		[29, 54, 67, 104],
		[30, 53, 64, 107],
		[31, 52, 65, 106]
	],

	[
		[128, 44, 93, 113],
		[1, 45, 92, 112],
		[2, 46, 95, 115],
		[3, 47, 94, 114],
		[4, 40, 89, 117],
		[5, 41, 88, 116],
		[6, 42, 91, 119],
		[7, 43, 90, 118],
		[8, 36, 85, 121],
		[9, 37, 84, 120],
		[10, 38, 87, 123],
		[11, 39, 86, 122],
		[12, 32, 81, 125],
		[13, 33, 80, 124],
		[14, 34, 83, 127],
		[15, 35, 82, 126],
		[16, 60, 77, 97],
		[17, 61, 76, 96],
		[18, 62, 79, 99],
		[19, 63, 78, 98],
		[20, 56, 73, 101],
		[21, 57, 72, 100],
		[22, 58, 75, 103],
		[23, 59, 74, 102],
		[24, 52, 69, 105],
		[25, 53, 68, 104],
		[26, 54, 71, 107],
		[27, 55, 70, 106],
		[28, 48, 65, 109],
		[29, 49, 64, 108],
		[30, 50, 67, 111],
		[31, 51, 66, 110]
	],

	[
		[128, 45, 95, 114],
		[1, 44, 94, 115],
		[2, 47, 93, 112],
		[3, 46, 92, 113],
		[4, 41, 91, 118],
		[5, 40, 90, 119],
		[6, 43, 89, 116],
		[7, 42, 88, 117],
		[8, 37, 87, 122],
		[9, 36, 86, 123],
		[10, 39, 85, 120],
		[11, 38, 84, 121],
		[12, 33, 83, 126],
		[13, 32, 82, 127],
		[14, 35, 81, 124],
		[15, 34, 80, 125],
		[16, 61, 79, 98],
		[17, 60, 78, 99],
		[18, 63, 77, 96],
		[19, 62, 76, 97],
		[20, 57, 75, 102],
		[21, 56, 74, 103],
		[22, 59, 73, 100],
		[23, 58, 72, 101],
		[24, 53, 71, 106],
		[25, 52, 70, 107],
		[26, 55, 69, 104],
		[27, 54, 68, 105],
		[28, 49, 67, 110],
		[29, 48, 66, 111],
		[30, 51, 65, 108],
		[31, 50, 64, 109]
	],

	[
		[128, 46, 89, 119],
		[1, 47, 88, 118],
		[2, 44, 91, 117],
		[3, 45, 90, 116],
		[4, 42, 93, 115],
		[5, 43, 92, 114],
		[6, 40, 95, 113],
		[7, 41, 94, 112],
		[8, 38, 81, 127],
		[9, 39, 80, 126],
		[10, 36, 83, 125],
		[11, 37, 82, 124],
		[12, 34, 85, 123],
		[13, 35, 84, 122],
		[14, 32, 87, 121],
		[15, 33, 86, 120],
		[16, 62, 73, 103],
		[17, 63, 72, 102],
		[18, 60, 75, 101],
		[19, 61, 74, 100],
		[20, 58, 77, 99],
		[21, 59, 76, 98],
		[22, 56, 79, 97],
		[23, 57, 78, 96],
		[24, 54, 65, 111],
		[25, 55, 64, 110],
		[26, 52, 67, 109],
		[27, 53, 66, 108],
		[28, 50, 69, 107],
		[29, 51, 68, 106],
		[30, 48, 71, 105],
		[31, 49, 70, 104]
	],

	[
		[128, 47, 91, 116],
		[1, 46, 90, 117],
		[2, 45, 89, 118],
		[3, 44, 88, 119],
		[4, 43, 95, 112],
		[5, 42, 94, 113],
		[6, 41, 93, 114],
		[7, 40, 92, 115],
		[8, 39, 83, 124],
		[9, 38, 82, 125],
		[10, 37, 81, 126],
		[11, 36, 80, 127],
		[12, 35, 87, 120],
		[13, 34, 86, 121],
		[14, 33, 85, 122],
		[15, 32, 84, 123],
		[16, 63, 75, 100],
		[17, 62, 74, 101],
		[18, 61, 73, 102],
		[19, 60, 72, 103],
		[20, 59, 79, 96],
		[21, 58, 78, 97],
		[22, 57, 77, 98],
		[23, 56, 76, 99],
		[24, 55, 67, 108],
		[25, 54, 66, 109],
		[26, 53, 65, 110],
		[27, 52, 64, 111],
		[28, 51, 71, 104],
		[29, 50, 70, 105],
		[30, 49, 69, 106],
		[31, 48, 68, 107]
	],

	[
		[128, 48, 72, 120],
		[1, 49, 73, 121],
		[2, 50, 74, 122],
		[3, 51, 75, 123],
		[4, 52, 76, 124],
		[5, 53, 77, 125],
		[6, 54, 78, 126],
		[7, 55, 79, 127],
		[8, 56, 64, 112],
		[9, 57, 65, 113],
		[10, 58, 66, 114],
		[11, 59, 67, 115],
		[12, 60, 68, 116],
		[13, 61, 69, 117],
		[14, 62, 70, 118],
		[15, 63, 71, 119],
		[16, 32, 88, 104],
		[17, 33, 89, 105],
		[18, 34, 90, 106],
		[19, 35, 91, 107],
		[20, 36, 92, 108],
		[21, 37, 93, 109],
		[22, 38, 94, 110],
		[23, 39, 95, 111],
		[24, 40, 80, 96],
		[25, 41, 81, 97],
		[26, 42, 82, 98],
		[27, 43, 83, 99],
		[28, 44, 84, 100],
		[29, 45, 85, 101],
		[30, 46, 86, 102],
		[31, 47, 87, 103]
	],

	[
		[128, 49, 74, 123],
		[1, 48, 75, 122],
		[2, 51, 72, 121],
		[3, 50, 73, 120],
		[4, 53, 78, 127],
		[5, 52, 79, 126],
		[6, 55, 76, 125],
		[7, 54, 77, 124],
		[8, 57, 66, 115],
		[9, 56, 67, 114],
		[10, 59, 64, 113],
		[11, 58, 65, 112],
		[12, 61, 70, 119],
		[13, 60, 71, 118],
		[14, 63, 68, 117],
		[15, 62, 69, 116],
		[16, 33, 90, 107],
		[17, 32, 91, 106],
		[18, 35, 88, 105],
		[19, 34, 89, 104],
		[20, 37, 94, 111],
		[21, 36, 95, 110],
		[22, 39, 92, 109],
		[23, 38, 93, 108],
		[24, 41, 82, 99],
		[25, 40, 83, 98],
		[26, 43, 80, 97],
		[27, 42, 81, 96],
		[28, 45, 86, 103],
		[29, 44, 87, 102],
		[30, 47, 84, 101],
		[31, 46, 85, 100]
	],

	[
		[128, 50, 76, 126],
		[1, 51, 77, 127],
		[2, 48, 78, 124],
		[3, 49, 79, 125],
		[4, 54, 72, 122],
		[5, 55, 73, 123],
		[6, 52, 74, 120],
		[7, 53, 75, 121],
		[8, 58, 68, 118],
		[9, 59, 69, 119],
		[10, 56, 70, 116],
		[11, 57, 71, 117],
		[12, 62, 64, 114],
		[13, 63, 65, 115],
		[14, 60, 66, 112],
		[15, 61, 67, 113],
		[16, 34, 92, 110],
		[17, 35, 93, 111],
		[18, 32, 94, 108],
		[19, 33, 95, 109],
		[20, 38, 88, 106],
		[21, 39, 89, 107],
		[22, 36, 90, 104],
		[23, 37, 91, 105],
		[24, 42, 84, 102],
		[25, 43, 85, 103],
		[26, 40, 86, 100],
		[27, 41, 87, 101],
		[28, 46, 80, 98],
		[29, 47, 81, 99],
		[30, 44, 82, 96],
		[31, 45, 83, 97]
	],

	[
		[128, 51, 78, 125],
		[1, 50, 79, 124],
		[2, 49, 76, 127],
		[3, 48, 77, 126],
		[4, 55, 74, 121],
		[5, 54, 75, 120],
		[6, 53, 72, 123],
		[7, 52, 73, 122],
		[8, 59, 70, 117],
		[9, 58, 71, 116],
		[10, 57, 68, 119],
		[11, 56, 69, 118],
		[12, 63, 66, 113],
		[13, 62, 67, 112],
		[14, 61, 64, 115],
		[15, 60, 65, 114],
		[16, 35, 94, 109],
		[17, 34, 95, 108],
		[18, 33, 92, 111],
		[19, 32, 93, 110],
		[20, 39, 90, 105],
		[21, 38, 91, 104],
		[22, 37, 88, 107],
		[23, 36, 89, 106],
		[24, 43, 86, 101],
		[25, 42, 87, 100],
		[26, 41, 84, 103],
		[27, 40, 85, 102],
		[28, 47, 82, 97],
		[29, 46, 83, 96],
		[30, 45, 80, 99],
		[31, 44, 81, 98]
	],

	[
		[128, 52, 77, 121],
		[1, 53, 76, 120],
		[2, 54, 79, 123],
		[3, 55, 78, 122],
		[4, 48, 73, 125],
		[5, 49, 72, 124],
		[6, 50, 75, 127],
		[7, 51, 74, 126],
		[8, 60, 69, 113],
		[9, 61, 68, 112],
		[10, 62, 71, 115],
		[11, 63, 70, 114],
		[12, 56, 65, 117],
		[13, 57, 64, 116],
		[14, 58, 67, 119],
		[15, 59, 66, 118],
		[16, 36, 93, 105],
		[17, 37, 92, 104],
		[18, 38, 95, 107],
		[19, 39, 94, 106],
		[20, 32, 89, 109],
		[21, 33, 88, 108],
		[22, 34, 91, 111],
		[23, 35, 90, 110],
		[24, 44, 85, 97],
		[25, 45, 84, 96],
		[26, 46, 87, 99],
		[27, 47, 86, 98],
		[28, 40, 81, 101],
		[29, 41, 80, 100],
		[30, 42, 83, 103],
		[31, 43, 82, 102]
	],

	[
		[128, 53, 79, 122],
		[1, 52, 78, 123],
		[2, 55, 77, 120],
		[3, 54, 76, 121],
		[4, 49, 75, 126],
		[5, 48, 74, 127],
		[6, 51, 73, 124],
		[7, 50, 72, 125],
		[8, 61, 71, 114],
		[9, 60, 70, 115],
		[10, 63, 69, 112],
		[11, 62, 68, 113],
		[12, 57, 67, 118],
		[13, 56, 66, 119],
		[14, 59, 65, 116],
		[15, 58, 64, 117],
		[16, 37, 95, 106],
		[17, 36, 94, 107],
		[18, 39, 93, 104],
		[19, 38, 92, 105],
		[20, 33, 91, 110],
		[21, 32, 90, 111],
		[22, 35, 89, 108],
		[23, 34, 88, 109],
		[24, 45, 87, 98],
		[25, 44, 86, 99],
		[26, 47, 85, 96],
		[27, 46, 84, 97],
		[28, 41, 83, 102],
		[29, 40, 82, 103],
		[30, 43, 81, 100],
		[31, 42, 80, 101]
	],

	[
		[128, 54, 73, 127],
		[1, 55, 72, 126],
		[2, 52, 75, 125],
		[3, 53, 74, 124],
		[4, 50, 77, 123],
		[5, 51, 76, 122],
		[6, 48, 79, 121],
		[7, 49, 78, 120],
		[8, 62, 65, 119],
		[9, 63, 64, 118],
		[10, 60, 67, 117],
		[11, 61, 66, 116],
		[12, 58, 69, 115],
		[13, 59, 68, 114],
		[14, 56, 71, 113],
		[15, 57, 70, 112],
		[16, 38, 89, 111],
		[17, 39, 88, 110],
		[18, 36, 91, 109],
		[19, 37, 90, 108],
		[20, 34, 93, 107],
		[21, 35, 92, 106],
		[22, 32, 95, 105],
		[23, 33, 94, 104],
		[24, 46, 81, 103],
		[25, 47, 80, 102],
		[26, 44, 83, 101],
		[27, 45, 82, 100],
		[28, 42, 85, 99],
		[29, 43, 84, 98],
		[30, 40, 87, 97],
		[31, 41, 86, 96]
	],

	[
		[128, 55, 75, 124],
		[1, 54, 74, 125],
		[2, 53, 73, 126],
		[3, 52, 72, 127],
		[4, 51, 79, 120],
		[5, 50, 78, 121],
		[6, 49, 77, 122],
		[7, 48, 76, 123],
		[8, 63, 67, 116],
		[9, 62, 66, 117],
		[10, 61, 65, 118],
		[11, 60, 64, 119],
		[12, 59, 71, 112],
		[13, 58, 70, 113],
		[14, 57, 69, 114],
		[15, 56, 68, 115],
		[16, 39, 91, 108],
		[17, 38, 90, 109],
		[18, 37, 89, 110],
		[19, 36, 88, 111],
		[20, 35, 95, 104],
		[21, 34, 94, 105],
		[22, 33, 93, 106],
		[23, 32, 92, 107],
		[24, 47, 83, 100],
		[25, 46, 82, 101],
		[26, 45, 81, 102],
		[27, 44, 80, 103],
		[28, 43, 87, 96],
		[29, 42, 86, 97],
		[30, 41, 85, 98],
		[31, 40, 84, 99]
	],

	[
		[128, 1, 3, 18],
		[2, 16, 17, 19],
		[4, 6, 7, 21],
		[5, 20, 22, 23],
		[8, 11, 25, 26],
		[9, 10, 24, 27],
		[12, 29, 30, 31],
		[13, 14, 15, 28],
		[32, 33, 35, 50],
		[34, 48, 49, 51],
		[36, 38, 39, 53],
		[37, 52, 54, 55],
		[40, 43, 57, 58],
		[41, 42, 56, 59],
		[44, 61, 62, 63],
		[45, 46, 47, 60],
		[64, 65, 67, 82],
		[66, 80, 81, 83],
		[68, 70, 71, 85],
		[69, 84, 86, 87],
		[72, 75, 89, 90],
		[73, 74, 88, 91],
		[76, 93, 94, 95],
		[77, 78, 79, 92],
		[96, 97, 99, 114],
		[98, 112, 113, 115],
		[100, 102, 103, 117],
		[101, 116, 118, 119],
		[104, 107, 121, 122],
		[105, 106, 120, 123],
		[108, 125, 126, 127],
		[109, 110, 111, 124]
	],

	[
		[128, 9, 17, 26],
		[1, 10, 16, 25],
		[2, 3, 8, 27],
		[11, 18, 19, 24],
		[4, 5, 13, 30],
		[14, 20, 21, 29],
		[6, 23, 28, 31],
		[7, 12, 15, 22],
		[32, 41, 49, 58],
		[33, 42, 48, 57],
		[34, 35, 40, 59],
		[43, 50, 51, 56],
		[36, 37, 45, 62],
		[46, 52, 53, 61],
		[38, 55, 60, 63],
		[39, 44, 47, 54],
		[64, 73, 81, 90],
		[65, 74, 80, 89],
		[66, 67, 72, 91],
		[75, 82, 83, 88],
		[68, 69, 77, 94],
		[78, 84, 85, 93],
		[70, 87, 92, 95],
		[71, 76, 79, 86],
		[96, 105, 113, 122],
		[97, 106, 112, 121],
		[98, 99, 104, 123],
		[107, 114, 115, 120],
		[100, 101, 109, 126],
		[110, 116, 117, 125],
		[102, 119, 124, 127],
		[103, 108, 111, 118]
	],

	[
		[128, 2, 12, 14],
		[16, 18, 28, 30],
		[1, 15, 19, 29],
		[3, 13, 17, 31],
		[4, 22, 24, 26],
		[6, 8, 10, 20],
		[5, 7, 25, 27],
		[9, 11, 21, 23],
		[32, 34, 44, 46],
		[48, 50, 60, 62],
		[33, 47, 51, 61],
		[35, 45, 49, 63],
		[36, 54, 56, 58],
		[38, 40, 42, 52],
		[37, 39, 57, 59],
		[41, 43, 53, 55],
		[64, 66, 76, 78],
		[80, 82, 92, 94],
		[65, 79, 83, 93],
		[67, 77, 81, 95],
		[68, 86, 88, 90],
		[70, 72, 74, 84],
		[69, 71, 89, 91],
		[73, 75, 85, 87],
		[96, 98, 108, 110],
		[112, 114, 124, 126],
		[97, 111, 115, 125],
		[99, 109, 113, 127],
		[100, 118, 120, 122],
		[102, 104, 106, 116],
		[101, 103, 121, 123],
		[105, 107, 117, 119]
	],

	[
		[128, 4, 19, 23],
		[3, 7, 16, 20],
		[1, 2, 5, 6],
		[17, 18, 21, 22],
		[8, 9, 12, 13],
		[24, 25, 28, 29],
		[10, 11, 15, 30],
		[14, 26, 27, 31],
		[32, 36, 51, 55],
		[35, 39, 48, 52],
		[33, 34, 37, 38],
		[49, 50, 53, 54],
		[40, 41, 44, 45],
		[56, 57, 60, 61],
		[42, 43, 47, 62],
		[46, 58, 59, 63],
		[64, 68, 83, 87],
		[67, 71, 80, 84],
		[65, 66, 69, 70],
		[81, 82, 85, 86],
		[72, 73, 76, 77],
		[88, 89, 92, 93],
		[74, 75, 79, 94],
		[78, 90, 91, 95],
		[96, 100, 115, 119],
		[99, 103, 112, 116],
		[97, 98, 101, 102],
		[113, 114, 117, 118],
		[104, 105, 108, 109],
		[120, 121, 124, 125],
		[106, 107, 111, 126],
		[110, 122, 123, 127]
	],

	[
		[128, 13, 20, 25],
		[4, 9, 16, 29],
		[1, 21, 26, 30],
		[5, 10, 14, 17],
		[2, 11, 22, 31],
		[6, 15, 18, 27],
		[3, 12, 23, 24],
		[7, 8, 19, 28],
		[32, 45, 52, 57],
		[36, 41, 48, 61],
		[33, 53, 58, 62],
		[37, 42, 46, 49],
		[34, 43, 54, 63],
		[38, 47, 50, 59],
		[35, 44, 55, 56],
		[39, 40, 51, 60],
		[64, 77, 84, 89],
		[68, 73, 80, 93],
		[65, 85, 90, 94],
		[69, 74, 78, 81],
		[66, 75, 86, 95],
		[70, 79, 82, 91],
		[67, 76, 87, 88],
		[71, 72, 83, 92],
		[96, 109, 116, 121],
		[100, 105, 112, 125],
		[97, 117, 122, 126],
		[101, 106, 110, 113],
		[98, 107, 118, 127],
		[102, 111, 114, 123],
		[99, 108, 119, 120],
		[103, 104, 115, 124]
	],

	[
		[128, 8, 15, 21],
		[5, 16, 24, 31],
		[1, 9, 22, 28],
		[6, 12, 17, 25],
		[2, 10, 23, 29],
		[7, 13, 18, 26],
		[3, 4, 11, 14],
		[19, 20, 27, 30],
		[32, 40, 47, 53],
		[37, 48, 56, 63],
		[33, 41, 54, 60],
		[38, 44, 49, 57],
		[34, 42, 55, 61],
		[39, 45, 50, 58],
		[35, 36, 43, 46],
		[51, 52, 59, 62],
		[64, 72, 79, 85],
		[69, 80, 88, 95],
		[65, 73, 86, 92],
		[70, 76, 81, 89],
		[66, 74, 87, 93],
		[71, 77, 82, 90],
		[67, 68, 75, 78],
		[83, 84, 91, 94],
		[96, 104, 111, 117],
		[101, 112, 120, 127],
		[97, 105, 118, 124],
		[102, 108, 113, 121],
		[98, 106, 119, 125],
		[103, 109, 114, 122],
		[99, 100, 107, 110],
		[115, 116, 123, 126]
	],

	[
		[128, 5, 11, 28],
		[12, 16, 21, 27],
		[1, 4, 8, 31],
		[15, 17, 20, 24],
		[2, 7, 9, 30],
		[14, 18, 23, 25],
		[3, 6, 26, 29],
		[10, 13, 19, 22],
		[32, 37, 43, 60],
		[44, 48, 53, 59],
		[33, 36, 40, 63],
		[47, 49, 52, 56],
		[34, 39, 41, 62],
		[46, 50, 55, 57],
		[35, 38, 58, 61],
		[42, 45, 51, 54],
		[64, 69, 75, 92],
		[76, 80, 85, 91],
		[65, 68, 72, 95],
		[79, 81, 84, 88],
		[66, 71, 73, 94],
		[78, 82, 87, 89],
		[67, 70, 90, 93],
		[74, 77, 83, 86],
		[96, 101, 107, 124],
		[108, 112, 117, 123],
		[97, 100, 104, 127],
		[111, 113, 116, 120],
		[98, 103, 105, 126],
		[110, 114, 119, 121],
		[99, 102, 122, 125],
		[106, 109, 115, 118]
	],

	[
		[128, 6, 24, 30],
		[8, 14, 16, 22],
		[1, 13, 23, 27],
		[7, 11, 17, 29],
		[2, 20, 26, 28],
		[4, 10, 12, 18],
		[3, 5, 9, 15],
		[19, 21, 25, 31],
		[32, 38, 56, 62],
		[40, 46, 48, 54],
		[33, 45, 55, 59],
		[39, 43, 49, 61],
		[34, 52, 58, 60],
		[36, 42, 44, 50],
		[35, 37, 41, 47],
		[51, 53, 57, 63],
		[64, 70, 88, 94],
		[72, 78, 80, 86],
		[65, 77, 87, 91],
		[71, 75, 81, 93],
		[66, 84, 90, 92],
		[68, 74, 76, 82],
		[67, 69, 73, 79],
		[83, 85, 89, 95],
		[96, 102, 120, 126],
		[104, 110, 112, 118],
		[97, 109, 119, 123],
		[103, 107, 113, 125],
		[98, 116, 122, 124],
		[100, 106, 108, 114],
		[99, 101, 105, 111],
		[115, 117, 121, 127]
	],

	[
		[128, 22, 27, 29],
		[6, 11, 13, 16],
		[1, 7, 14, 24],
		[8, 17, 23, 30],
		[2, 4, 15, 25],
		[9, 18, 20, 31],
		[3, 10, 21, 28],
		[5, 12, 19, 26],
		[32, 54, 59, 61],
		[38, 43, 45, 48],
		[33, 39, 46, 56],
		[40, 49, 55, 62],
		[34, 36, 47, 57],
		[41, 50, 52, 63],
		[35, 42, 53, 60],
		[37, 44, 51, 58],
		[64, 86, 91, 93],
		[70, 75, 77, 80],
		[65, 71, 78, 88],
		[72, 81, 87, 94],
		[66, 68, 79, 89],
		[73, 82, 84, 95],
		[67, 74, 85, 92],
		[69, 76, 83, 90],
		[96, 118, 123, 125],
		[102, 107, 109, 112],
		[97, 103, 110, 120],
		[104, 113, 119, 126],
		[98, 100, 111, 121],
		[105, 114, 116, 127],
		[99, 106, 117, 124],
		[101, 108, 115, 122]
	],

	[
		[128, 7, 10, 31],
		[15, 16, 23, 26],
		[1, 11, 12, 20],
		[4, 17, 27, 28],
		[2, 13, 21, 24],
		[5, 8, 18, 29],
		[3, 22, 25, 30],
		[6, 9, 14, 19],
		[32, 39, 42, 63],
		[47, 48, 55, 58],
		[33, 43, 44, 52],
		[36, 49, 59, 60],
		[34, 45, 53, 56],
		[37, 40, 50, 61],
		[35, 54, 57, 62],
		[38, 41, 46, 51],
		[64, 71, 74, 95],
		[79, 80, 87, 90],
		[65, 75, 76, 84],
		[68, 81, 91, 92],
		[66, 77, 85, 88],
		[69, 72, 82, 93],
		[67, 86, 89, 94],
		[70, 73, 78, 83],
		[96, 103, 106, 127],
		[111, 112, 119, 122],
		[97, 107, 108, 116],
		[100, 113, 123, 124],
		[98, 109, 117, 120],
		[101, 104, 114, 125],
		[99, 118, 121, 126],
		[102, 105, 110, 115]
	]
]