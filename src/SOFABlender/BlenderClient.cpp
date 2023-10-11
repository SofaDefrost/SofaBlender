#include <sofa/component/visual/VisualModelImpl.h>
#include <sofa/core/ObjectFactory.h>
#include <SOFABlender/BlenderClient.h>
#include <sofa/simulation/AnimateBeginEvent.h>
#include <sofa/core/visual/VisualModel.h>
#include <sofa/helper/ScopedAdvancedTimer.h>
#include <SOFABlender/json/json.hpp>

namespace sofablender
{
int BlenderClientClass = sofa::core::RegisterObject("Client sending data to a Blender server")
    .add< BlenderClient >();

BlenderClient::BlenderClient()
    : d_host(initData(&d_host, std::string("127.0.0.1"), "host",
                      "Network address of the device running the server"))
    , d_port(initData(&d_port, 12345u, "port",
                      "Numeric value (ranging from 0 to 65535) identifying a communication channel with the server"))
    , m_socket(m_ioService)
{
    f_listening.setValue(true);
}

void BlenderClient::init()
{
    BaseObject::init();

    try
    {
        m_serverEndpoint = std::make_unique<boost::asio::ip::tcp::endpoint>(
            boost::asio::ip::address::from_string(d_host.getValue()), d_port.getValue());

        m_socket.connect(*m_serverEndpoint);
    }
    catch (std::exception& e)
    {
        msg_error() << "Initialization failed: " << e.what();
        this->d_componentState.setValue(sofa::core::objectmodel::ComponentState::Invalid);
        return;
    }

    sendData();
    ++m_nbIterations;

    this->d_componentState.setValue(sofa::core::objectmodel::ComponentState::Valid);
}

void BlenderClient::cleanup()
{
    BaseObject::cleanup();
    if (this->isComponentStateValid())
    {
        m_socket.close();
    }
}

void BlenderClient::handleEvent(sofa::core::objectmodel::Event* event)
{
    if (sofa::simulation::AnimateBeginEvent::checkEventType(event))
    {
        onBeginAnimationStep();
    }
}

void BlenderClient::sendHeader()
{
    std::stringstream header;
    header << "<SOFABlender>";

    boost::asio::write(m_socket, boost::asio::buffer(header.str()));
}

void BlenderClient::sendMesh(const sofa::core::visual::VisualModel* visualModel)
{
    std::stringstream serializedMesh;

    serializedMesh << "|";
    serializedMesh << visualModel->getName();
    serializedMesh << "%";

    boost::asio::write(m_socket, boost::asio::buffer(serializedMesh.str()));
}

void BlenderClient::sendFooter()
{
    boost::asio::write(m_socket, boost::asio::buffer("</SOFABlender>"));
}

void BlenderClient::sendSerializedMeshes(const std::string& serializedMeshes)
{
    std::size_t pos = 0;
    static constexpr std::size_t chunkSize = 4096;
    while (pos < serializedMeshes.length())
    {
        const std::string chunk = serializedMeshes.substr(pos, chunkSize);
        boost::asio::write(m_socket, boost::asio::buffer(chunk));
        pos += chunkSize;
    }
}

void BlenderClient::convertMeshesToJSON(const std::vector<sofa::component::visual::VisualModelImpl*>& visualModels, nlohmann::json& jsonMessage)
{
    nlohmann::json jsonMeshes = nlohmann::json::array();

    for (const auto& visualModel : visualModels)
    {
        if (visualModel->d_enable.getValue())
        {
            nlohmann::json jsonMesh;
            jsonMesh["name"] = visualModel->getName();
            jsonMesh["vertices"] = nlohmann::json(visualModel->m_positions.getValue());
            jsonMesh["faces"] = nlohmann::json(visualModel->getTriangles());
            jsonMeshes.push_back(jsonMesh);
        }
    }

    jsonMessage["iteration"] = m_nbIterations;
    jsonMessage["meshes"] = jsonMeshes;
}

void BlenderClient::sendData()
{
    if (!this->isComponentStateValid())
    {
        return;
    }

    SCOPED_TIMER("SendDataToBlender");

    const auto visualModels = this->getContext()->getObjects<sofa::component::visual::VisualModelImpl>(sofa::core::objectmodel::BaseContext::SearchDown);
    sendHeader();
    {
        nlohmann::json jsonMessage;
        convertMeshesToJSON(visualModels, jsonMessage);

        sendSerializedMeshes(jsonMessage.dump());
    }
    sendFooter();
}

void BlenderClient::onBeginAnimationStep()
{
    sendData();
    ++m_nbIterations;
}


}
