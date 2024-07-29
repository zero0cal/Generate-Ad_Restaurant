var project = app.project;

// 시퀀스를 가져오는 함수
function getSequenceByName(name) {
    for (var i = 0; i < project.sequences.length; i++) {
        if (project.sequences[i].name === name) {
            return project.sequences[i];
        }
    }
    return null;
}

// 새 시퀀스를 생성하는 함수
function createSequence(name, presetPath) {
    var presetFile = new File(presetPath);
    if (presetFile.exists) {
        app.enableQE();
        qe.project.newSequence(name, presetPath);
        return project.activeSequence;
    } else {
        throw new Error("Preset file not found: " + presetPath);
    }
}

function copyClips(sourceSequence, targetSequence) {
    var sourceTrack = sourceSequence.videoTracks[1];
    var targetTrack = targetSequence.videoTracks[1];

    for (var j = 0; j < sourceTrack.clips.numItems; j++) {
        var clip = sourceTrack.clips[j];
        var clipDuration = (clip.end.seconds - clip.start.seconds);
        targetTrack.insertClip(clip.projectItem, clip.start.ticks);
        var targetClip = targetTrack.clips[targetTrack.clips.numItems - 1];
        targetClip.end = targetClip.start.seconds + clipDuration;
    }
}

// 전환 효과
function applytransition(sequence_index) {
    var transformEffect = qe.project.getVideoEffectByName("방향 흐림");
    var transition_target = qe.project.getSequenceAt(sequence_index+1);

    for (var i = 1; i <= 5; i += 2) {
        var targetQEClip = transition_target.getVideoTrackAt(1).getItemAt(i);
        targetQEClip.addVideoEffect(transformEffect);

        var targetTransformEffect = targetQEClip.getComponentAt(2);

        var p_1 = "방향";
        var p_2 = "흐림 길이";
        var source_1 = "90";
        var source_2 = "70";

        targetTransformEffect.setParamValue(p_1, source_1);
        targetTransformEffect.setParamValue(p_2, source_2);
    }
}

// 시퀀스에서 모든 클립을 삭제하는 함수
function clearSequence(sequence) {
    if (!sequence) throw new Error("Active sequence is not available.");

    for (var i = 0; i < 1; i++) {
        var track = sequence.videoTracks[i];
        for (var j = track.clips.numItems - 1; j >= 0; j--) {
            track.clips[j].remove(0, 1);
        }
    }
    for (var i = 0; i < sequence.audioTracks.numTracks; i++) {
        var track = sequence.audioTracks[i];
        for (var j = track.clips.numItems - 1; j >= 0; j--) {
            track.clips[j].remove(0, 1);
        }
    }
}

function clear(sequence) {
    var track = sequence.videoTracks[0];
    for (var j = track.clips.numItems - 1; j >= 5; j--) {
        track.clips[j].remove(0, 1);
    }

    var audio_track = sequence.audioTracks[0];
    for (var j = audio_track.clips.numItems-1; j>0;j--){
        audio_track.clips[j].remove(0,1)
    }
}

// 파일을 가져와서 프로젝트에 추가하는 함수
function importFile(filepath) {
    var importSuccessful = app.project.importFiles([filepath], 1, project.rootItem, 0);
    if (importSuccessful) {
        var newItem = null;
        for (var i = 0; i < project.rootItem.children.numItems; i++) {
            var item = project.rootItem.children[i];
            if (item.getMediaPath() === filepath) {
                newItem = item;
                break;
            }
        }
        if (newItem) {
            return newItem;
        } else {
            alert("Imported file not found in project root: " + filepath);
            throw new Error("Imported file not found in project root: " + filepath);
        }
    } else {
        alert("File import failed: " + filepath);
        throw new Error("File import failed: " + filepath);
    }
}

// 타임라인에 클립을 추가하는 함수
function addClipToTimeline(clip, trackIndex, time, isAudio, startTime, endTime) {
    var sequence = project.activeSequence;
    if (!sequence) throw new Error("Active sequence is not available.");

    var newClip;
    if (isAudio) {
        var audioTrack = sequence.audioTracks[trackIndex];
        if (!audioTrack) throw new Error("Audio track " + trackIndex + " not found.");
        newClip = audioTrack.insertClip(clip, time);
    } else {
        var videoTrack = sequence.videoTracks[trackIndex];
        if (!videoTrack) throw new Error("Video track " + trackIndex + " not found.");
        newClip = videoTrack.insertClip(clip, time);
    }
    

    if (startTime !== undefined && endTime !== undefined) {
        var music_track_clip = sequence.audioTracks[trackIndex].clips[0];
        music_track_clip.inPoint = startTime;
        music_track_clip.outPoint = endTime;
    }
}
// 특정 클립에 효과를 추가하고 비율을 조정하는 함수
function adjustClipProperties(clip, scale, position) {
    var components = clip.components;
    components[1].properties[1].setValue(scale);
}

// audioVolume 조절
function adjustClipVolume(clip, decibels) {
    var components = clip.components;
    components[0].properties[1].setValue(decibels);
}

// 특정 클립을 특정 시간에 맞게 자르는 함수
function trimClip(clip, newOutPoint) {
    clip.end = newOutPoint;
}

// 자막 파일 읽기 함수
function readSrtFile(filepath) {
    var file = File(filepath);

    if (!file.exists) {
        alert("SRT 파일을 찾을 수 없습니다.");
    }

    file.open("r");
    var lines = file.read().split("\n");
    file.close();

    var subtitles = [];
    var subtitle = {};

    for (var i = 0; i < lines.length; i++) {
        var line = lines[i].trim();
        if (!isNaN(line)) {
            if (subtitle.start) subtitles.push(subtitle);
            subtitle = { text: "" };
        } else if (line.indexOf("-->") !== -1) {
            var times = line.split(" --> ");
            subtitle.start = timeStringToSeconds(times[0]);
            subtitle.end = timeStringToSeconds(times[1]);
        } else {
            if (subtitle.text) subtitle.text += "\n";
            subtitle.text += line;
        }
    }
    if (subtitle.start) subtitles.push(subtitle);
    return subtitles;
}

function timeStringToSeconds(timeString) {
    var parts = timeString.split(":");
    var seconds = parseFloat(parts[2].replace(",", "."));

    seconds += parseInt(parts[1]) * 60;
    seconds += parseInt(parts[0]) * 3600;

    return seconds;
}

function applySubtitle(srtFile, mogrtFile) {
    var project = app.project;
    var sequence = project.activeSequence;
    subtitles = readSrtFile(srtFile);
    for (var i = 0; i < subtitles.length; i++) {
        var subtitle = subtitles[i];
        
        sequence.importMGT(mogrtFile.fsName, subtitle.start, 2, 2);
        var mgt = sequence.videoTracks[2].clips[i];
        
        alert(subtitle.start)
        mgt.end = subtitle.end;

        var property = mgt.getMGTComponent().properties;
        property.getParamForDisplayName("배달의민족 주아").setValue(subtitle.text);
    }
}

function generateAd(restaurant_name, index) {
    //Video
    var video_baseDir = "/Users/zero/STUDY/UGRP/gummy_Video/Restaurant/" + restaurant_name + "/Video/";
    var videoFile_1 = video_baseDir + restaurant_name + "_1.mp4";
    var videoFile_2 = video_baseDir + restaurant_name + "_2.mp4";
    var videoFile_3 = video_baseDir + restaurant_name + "_3.mp4";
    var videoFile_4 = video_baseDir + restaurant_name + "_4.mp4";

    //Script 
    var script_baseDir = "/Users/zero/STUDY/UGRP/gummy_Video/Restaurant/" + restaurant_name + "/Source/"
    var srt = script_baseDir + restaurant_name + "_promo_reel.srt";
    var narrationFile = script_baseDir + restaurant_name + "_promo_reel.mp3";

    var mogrt = "/Users/zero/STUDY/UGRP/gummy_Video/Common_File/Font/gummy_font_주아_mid.mogrt";
    var gummyGraphic = "/Users/zero/STUDY/UGRP/gummy_Video/Common_File/WaterMark/Gummy_Graphic.mp4";
    var musicFile_list = ["/Users/zero/STUDY/UGRP/gummy_Video/Common_File/Music/0719_music.mp3",
                    "/Users/zero/STUDY/UGRP/gummy_Video/Common_File/Music/0720_music.mp3",
                    "/Users/zero/STUDY/UGRP/gummy_Video/Common_File/Music/0721_music.mp3",
                    "/Users/zero/STUDY/UGRP/gummy_Video/Common_File/Music/0722_music.mp3",
                    "/Users/zero/STUDY/UGRP/gummy_Video/Common_File/Music/0723_music.mp3"];

    try {
        if (!project) throw new Error("Project is not open.");

        var originalSequenceName = "조정레이어";
        var newSequenceName = restaurant_name + " Sequence";
        var sequencePresetPath = "/Users/zero/Documents/Adobe/Premiere Pro/24.0/Profile-zero/Settings/GummyDefined/gummy_shorts.sqpreset";
        
        //musicFile 선택 및 구간 조정
        if(index%10 == 0){
            music_marker = 0;
        }else{
            music_marker += 1;
        }
        var musicFile = musicFile_list[(index/10) | 0];

        var originalSequence = getSequenceByName(originalSequenceName);
        if (!originalSequence) throw new Error("Original sequence not found.");

        var duplicatedSequence = createSequence(newSequenceName, sequencePresetPath);
        if (!duplicatedSequence) throw new Error("Failed to create duplicated sequence.");

        copyClips(originalSequence, duplicatedSequence);
        applytransition(index);

        var sequence = project.activeSequence;
        if (!sequence) throw new Error("No active sequence found.");

        var videoClip_1 = importFile(videoFile_1);
        var videoClip_2 = importFile(videoFile_2);
        var videoClip_3 = importFile(videoFile_3);
        var videoClip_4 = importFile(videoFile_4);
        var gummyClip = importFile(gummyGraphic);
        var audioClip = importFile(musicFile);
        var narrationClip = importFile(narrationFile);

        addClipToTimeline(videoClip_1, 0, 0, false);
        addClipToTimeline(videoClip_2, 0, 4, false);
        addClipToTimeline(videoClip_3, 0, 8, false);
        addClipToTimeline(videoClip_4, 0, 12, false);
        addClipToTimeline(gummyClip, 0, 16, false);


        //musicFile import 
        //offset이 구간 설정
        music_offset = 18.0; 
        addClipToTimeline(audioClip, 0, 0, true, 18.0*music_marker, 18.0*music_marker+music_offset);
        addClipToTimeline(narrationClip, 1, 0, true);

        //클립의 스케일 조정
        adjustClipProperties(sequence.videoTracks[0].clips[0], 165);
        adjustClipProperties(sequence.videoTracks[0].clips[1], 165);
        adjustClipProperties(sequence.videoTracks[0].clips[2], 165);
        adjustClipProperties(sequence.videoTracks[0].clips[3], 165);

        var audioTrack = sequence.audioTracks[0];
        var audioTrack_2 = sequence.audioTracks[1];

        var audio_firstClip = audioTrack.clips[0];
        var audio_secondClip = audioTrack_2.clips[0];

        var video_gummyClip = sequence.videoTracks[0].clips[4]

        var newOutPoint = 18.0;
        var narration_endPoint = audio_secondClip.end.seconds;

        //narration 너무 길 경우(outlier), 그래픽 조정
        if(narration_endPoint > newOutPoint){
            newOutPoint = narration_endPoint;
        }
        
        trimClip(audio_firstClip, newOutPoint);
        trimClip(video_gummyClip, newOutPoint);

        adjustClipVolume(audio_firstClip, 0.01100);

        clear(sequence);
        applySubtitle(srt, File(mogrt));
    } catch (e) {
        alert("Error processing " + restaurant_name + ": " + e.message);
    }
}

// 텍스트 파일을 읽어 레스토랑 이름을 처리하는 함수
function generateAdNamesFromFile(filepath) {
    var file = File(filepath);
    if (!file.exists) {
        alert("Restaurant names file not found: " + filepath);
        return;
    }

    file.open("r");
    var restaurantNames = file.read().split("\n");
    file.close();

    for (var i = 0; i < 50 && i < restaurantNames.length; i++) {
        var restaurantName = restaurantNames[i].trim();
        if (restaurantName) {
            generateAd(restaurantName, i);
        }
    }
}

var restaurantNamesFilePath = "/Users/zero/STUDY/UGRP/Google Cloud/restaurant_List.txt";
generateAdNamesFromFile(restaurantNamesFilePath);
