var project = app.project;

// AME(Adobe Media Encoder) 경로 설정
var presetPath = "/Users/zero/STUDY/UGRP/gummy_Video/Common_File/Encoder/Gummy_Short_ver1.epr"; // 내보내기 프리셋 파일 경로를 설정

function exportSequence(sequence, index, restaurant_name, outputPath) {
    var outputFilename = outputPath + restaurant_name + ".mp4"; // 출력 파일명 설정 (원하는 형식으로 변경 가능)

    var amepath = new File("/Applications/Adobe Media Encoder 2024/Adobe Media Encoder 2024.app");

    if (amepath.exists) {
        var outputFolder = new Folder(outputPath);
        if (!outputFolder.exists) {
            outputFolder.create();
        }

        app.encoder.launchEncoder();

        // AME에 내보내기 작업 추가
        app.encoder.encodeSequence(
            sequence,
            outputFilename,
            presetPath,
            app.encoder.ENCODE_WORKAREA
        );

    } else {
        console.error("Adobe Media Encoder not found. Please check the path.");
    }
}

// 내보내기 완료 시 호출되는 함수
function onEncoderJobComplete(jobID) {
    console.log("Export complete: " + jobID);
}

// 내보내기 오류 시 호출되는 함수
function onEncoderJobError(jobID, errorMessage) {
    console.error("Export error: " + jobID + " - " + errorMessage);
}

// 텍스트 파일을 읽어, 레스토랑 이름 Sequence 처리
function encoder() {
    app.encoder.bind('onEncoderJobComplete', onEncoderJobComplete);
    app.encoder.bind('onEncoderJobError', onEncoderJobError);

    for (var i = 0; i < project.sequences.length; i++) {
        var sequence = project.sequences[i];

        if (sequence.name === "조정레이어") continue;

        var restaurant_name = sequence.name.replace(/ Sequence$/, "");
        var outputPath = "/Users/zero/STUDY/UGRP/gummy_Video/final_Video/" + restaurant_name + "/"; // 출력 폴더 경로 설정

        if (sequence) {
            exportSequence(sequence, i, restaurant_name, outputPath);
        } else {
            console.warn("Sequence " + i + " not found.");
        }
    }

    //자동 실행
    app.encoder.startBatch();
}

encoder();
